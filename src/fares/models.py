from django_sorcery.db import databases
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, DateTime, select, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import coalesce

db = databases.get("default")


class IdMixin:
    id = db.Column(db.Integer, primary_key=True)


class Airline(IdMixin, db.Model):
    __tablename__ = "airline"

    name = db.Column(String(), nullable=False)
    iata = db.Column(String())
    icao = db.Column(String())


class Airport(IdMixin, db.Model):
    __tablename__ = "airport"

    name = db.Column(String(), nullable=False)
    tz_offset = db.Column(Numeric())
    tz = db.Column(String())
    iata = db.Column(String())
    icao = db.Column(String())


class SearchRequest(IdMixin, db.Model):
    __tablename__ = 'fares_search_request'

    partner_request_id = db.Column(db.String(), nullable=False)
    partner_tag = db.Column(String(), nullable=False)


class Flight(IdMixin, db.Model):
    __tablename__ = 'fares_flight'

    order = Column(SmallInteger, nullable=False)
    trip_id = Column(Integer, ForeignKey('fares_trip.id'), nullable=False, index=True)
    trip = relationship('Trip', back_populates='flights')

    carrier_id = Column(Integer, ForeignKey('airline.id'), index=True)
    carrier = relationship(Airline, lazy="joined")

    flight_number = Column(String())
    source_id = Column(Integer, ForeignKey('airport.id'), nullable=False, index=True)
    source = relationship(Airport, foreign_keys=source_id, lazy="joined")
    destination_id = Column(Integer, ForeignKey('airport.id'), nullable=False, index=True)
    destination = relationship(Airport, foreign_keys=destination_id, lazy="joined")

    departure = Column(DateTime(timezone=True), nullable=False)
    arrival = Column(DateTime(timezone=True), nullable=False)

    service_class = Column(String())
    ticket_type = Column(String())

    number_of_stops = Column(Integer())
    fare_basis = Column(String())


class Trip(IdMixin, db.Model):
    __tablename__ = 'fares_trip'

    flights = relationship(Flight, order_by=Flight.order, back_populates='trip')

    @hybrid_property
    def source_iata(self):
        return self.flights[0].source.iata

    @source_iata.expression
    def source_iata(cls):
        return select([Airport.iata]).where(
            Airport.id == select([Flight.source_id]) \
            .where(Flight.trip_id == cls.id) \
            .order_by(Flight.order) \
            .limit(1) \
            .as_scalar()
        ).as_scalar()

    @hybrid_property
    def destination_iata(self):
        return self.flights[0].source.iata

    @destination_iata.expression
    def destination_iata(cls):
        return select([Airport.iata]).where(
            Airport.id == select([Flight.destination_id]) \
            .where(Flight.trip_id == cls.id) \
            .order_by(Flight.order.desc()) \
            .limit(1) \
            .as_scalar()
        ).as_scalar()

        # @hybrid_property
        # def destination(self):
        #     return self.flights[-1].destination
        #
        # @destination.expression
        # def destination(cls):
        #     return select([Flight.destination]) \
        #         .where(Flight.trip_id == cls.id) \
        #         .order_by(Flight.order.desc()) \
        #         .limit(1) \
        #         .as_scalar()

    @hybrid_property
    def duration(self):
        return self.flights[-1].arrival - self.flights[0].departure

    @duration.expression
    def duration(cls):
        return select([Flight.arrival]) \
                   .where(Flight.trip_id == cls.id) \
                   .order_by(Flight.order.desc()) \
                   .limit(1) \
                   .as_scalar() - \
               select([Flight.departure]) \
                   .where(Flight.trip_id == cls.id) \
                   .order_by(Flight.order) \
                   .limit(1) \
                   .as_scalar()


class Itinerary(IdMixin, db.Model):
    __tablename__ = 'fares_itinerary'

    request_id = db.Column(Integer, ForeignKey('fares_search_request.id'), nullable=False)
    request = relationship(SearchRequest)

    onward_trip_id = db.Column(Integer, ForeignKey('fares_trip.id'), nullable=False, index=True)
    onward_trip = relationship(Trip, foreign_keys=onward_trip_id)

    return_trip_id = db.Column(Integer, ForeignKey('fares_trip.id'), nullable=True, index=True)
    return_trip = relationship(Trip, foreign_keys=return_trip_id)

    price_adult = db.Column(db.Numeric)
    price_child = db.Column(db.Numeric)
    price_infant = db.Column(db.Numeric)
    price_details = db.Column(JSONB)

    @hybrid_method
    def price(self, adult=1, child=0, infant=0):
        return self.price_adult * adult \
               + (self.price_child or self.price_adult) * child \
               + (self.price_infant or self.price_adult) * infant

    @price.expression
    def price(cls, adult=1, child=0, infant=0):
        expr = cls.price_adult * adult
        if child:
            expr += coalesce(cls.price_child, cls.price_adult) * child
        if infant:
            expr += coalesce(cls.price_infant, cls.price_adult) * infant

        return expr
