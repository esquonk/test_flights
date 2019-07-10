from typing import TextIO

from lxml import etree

import dateutil.parser
from pytz import timezone

from db.fares.models import SearchRequest, Itinerary, Trip, Flight
from db.reference.models import Airline, Airport


class XmlImporter:
    def __init__(self, session, stream: TextIO, partner_tag: str):
        self.session = session
        self.stream = stream
        self.partner_tag = partner_tag

    def process_trip(self, tag):
        trip = Trip()
        self.session.add(trip)

        for i, flight_tag in enumerate(tag.findall("Flights/Flight")):
            source = self.session.query(Airport).filter(
                Airport.iata == flight_tag.find('Source').text.strip()
            ).first()

            destination = self.session.query(Airport).filter(
                Airport.iata == flight_tag.find('Destination').text.strip()
            ).first()

            if source is None or destination is None:
                # NOTE: airport not found, should probably log this somewhere
                continue

            if not destination.tz:
                print(destination.iata, destination.name)

            flight = Flight(
                trip=trip,
                carrier_id=self.session.query(Airline.id)
                    .filter(Airline.iata == flight_tag.find("Carrier").get('id')).first(),
                order=i,
                flight_number=flight_tag.find('FlightNumber').text.strip(),
                source=source,
                destination=destination,
                departure=timezone(source.tz).localize(
                    dateutil.parser.parse(flight_tag.find('DepartureTimeStamp').text.strip())
                ),
                arrival=timezone(destination.tz).localize(
                    dateutil.parser.parse(flight_tag.find('ArrivalTimeStamp').text.strip())
                ),
                service_class=flight_tag.find('Class').text.strip(),
                ticket_type=flight_tag.find('TicketType').text.strip(),
                fare_basis=flight_tag.find('FareBasis').text.strip(),
            )
            self.session.add(flight)

        return trip

    def process_itinerary(self, onward_tag, return_tag):
        itinerary = Itinerary(request=self.request)
        itinerary.onward_trip = self.process_trip(onward_tag)
        itinerary.return_trip = None if return_tag is None else self.process_trip(return_tag)

        return itinerary

    def run(self):
        tree = etree.parse(self.stream)

        self.request = SearchRequest(
            partner_request_id=tree.getroot().find('RequestId').text,
            partner_tag=self.partner_tag,
        )

        self.session.add(self.request)

        for flights_tag in tree.getroot().findall('PricedItineraries/Flights'):
            itinerary = self.process_itinerary(
                flights_tag.find('OnwardPricedItinerary'),
                flights_tag.find('ReturnPricedItinerary')
            )
            # print(itinerary, itinerary.onward_trip, itinerary.return_trip, itinerary.onward_trip)
