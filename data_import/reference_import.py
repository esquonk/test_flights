import os
import csv

from db.reference.models import Airport, Airline

checknull = lambda val: None if val == '\\N' else val


def import_airports():
    from db.engine import Session

    session = Session()

    with open(os.path.join('data', 'airports.dat'), newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key = int(row[0])

            airport = session.query(Airport).get(key)
            if airport is None:
                airport = Airport(id=key)
                session.add(airport)

            airport.name = row[1]
            airport.iata = checknull(row[4])
            airport.icao = checknull(row[5])
            airport.tz = checknull(row[11])

    session.commit()


def import_airlines():
    from db.engine import Session

    session = Session()

    with open(os.path.join('data', 'airlines.dat'), newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key = int(row[0])

            airline = session.query(Airline).get(key)
            if airline is None:
                airline = Airline(id=key)
                session.add(airline)

            airline.name = row[1]
            airline.iata = checknull(row[3])
            airline.icao = checknull(row[4])

    session.commit()
