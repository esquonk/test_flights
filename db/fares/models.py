from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger

from sqlalchemy.orm import relationship

from .. import Base


class IdMixin:
    id = Column(Integer, primary_key=True)


class SearchRequest(IdMixin, Base):
    __tablename__ = 'fares_search_request'

    partner_request_id = Column(String(), nullable=False)


class Trip(IdMixin, Base):
    __tablename__ = 'fares_trip'


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

    carrier_id = Column(String(2))