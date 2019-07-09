from sqlalchemy import Column, Integer, String

from db import Base


class Airline(Base):
    __tablename__ = "airline"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    iata = Column(String())
    icao = Column(String())


class Airport(Base):
    __tablename__ = "airport"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    tz = Column(String())
    iata = Column(String())
    icao = Column(String())
