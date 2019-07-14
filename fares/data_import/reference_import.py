import os
import csv

from fares.models import db, Airline, Airport

checknull = lambda val: None if val == '\\N' else val


def import_airports():
    timezones = {
        None: None
    }

    with open(os.path.join('data', 'iata.tzmap'), newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            timezones[row[0]] = row[1]

    with open(os.path.join('data', 'airports.dat'), newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key = int(row[0])

            airport = db.query(Airport).get(key)
            if airport is None:
                airport = Airport(id=key)
                db.add(airport)

            airport.name = row[1]
            airport.iata = checknull(row[4])
            airport.icao = checknull(row[5])
            airport.tz = checknull(row[11]) or timezones.get(airport.iata)

    db.commit()


def import_airlines():
    with open(os.path.join('data', 'airlines.dat'), newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key = int(row[0])

            airline = db.query(Airline).get(key)
            if airline is None:
                airline = Airline(id=key)
                db.add(airline)

            airline.name = row[1]
            airline.iata = checknull(row[3])
            airline.icao = checknull(row[4])

    db.commit()