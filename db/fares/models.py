from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, DateTime

from sqlalchemy.orm import relationship

from db.reference.models import Airline, Airport
from .. import Base


class IdMixin:
    id = Column(Integer, primary_key=True)


class SearchRequest(IdMixin, Base):
    __tablename__ = 'fares_search_request'

    partner_request_id = Column(String(), nullable=False)
    partner_tag = Column(String(), nullable=False)


class Trip(IdMixin, Base):
    __tablename__ = 'fares_trip'
    flights = relationship('Flight', order_by='Flight.order')


class Itinerary(IdMixin, Base):
    __tablename__ = 'fares_itinerary'

    request_id = Column(Integer, ForeignKey('fares_search_request.id'), nullable=False)
    request = relationship(SearchRequest)

    onward_trip_id = Column(Integer, ForeignKey('fares_trip.id'), nullable=False)
    onward_trip = relationship(Trip, primaryjoin=onward_trip_id == Trip.id)

    return_trip_id = Column(Integer, ForeignKey('fares_trip.id'), nullable=True)
    return_trip = relationship(Trip, primaryjoin=return_trip_id == Trip.id)


class Flight(IdMixin, Base):
    __tablename__ = 'fares_flight'

    order = Column(SmallInteger, nullable=False)
    trip_id = Column(Integer, ForeignKey('fares_trip.id'), nullable=False)
    trip = relationship(Trip)

    carrier_id = Column(Integer, ForeignKey('airline.id'))
    carrier = relationship(Airline)

    flight_number = Column(String())
    source_id = Column(Integer, ForeignKey('airport.id'), nullable=False)
    source = relationship(Airport, primaryjoin=source_id == Airport.id)
    destination_id = Column(Integer, ForeignKey('airport.id'), nullable=False)
    destination = relationship(Airport, primaryjoin=destination_id == Airport.id)

    departure = Column(DateTime(timezone=True), nullable=False)
    arrival = Column(DateTime(timezone=True), nullable=False)

    service_class = Column(String())
    ticket_type = Column(String())

    number_of_stops = Column(Integer())
    fare_basis = Column(String())