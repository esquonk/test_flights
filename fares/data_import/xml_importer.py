from decimal import Decimal
from typing import TextIO

from lxml import etree

import dateutil.parser
from pytz import timezone

from fares.models import SearchRequest, Itinerary, Trip, Flight, Airline, Airport, db


class XmlImporter:
    def __init__(self, stream: TextIO, partner_tag: str):
        self.stream = stream
        self.partner_tag = partner_tag

    def process_trip(self, tag):
        trip = Trip()
        db.add(trip)

        for i, flight_tag in enumerate(tag.findall("Flights/Flight")):
            source = db.query(Airport).filter(
                Airport.iata == flight_tag.find('Source').text.strip()
            ).first()

            destination = db.query(Airport).filter(
                Airport.iata == flight_tag.find('Destination').text.strip()
            ).first()

            if source is None or destination is None:
                # NOTE: airport not found, should probably log this somewhere
                continue

            if not destination.tz:
                print(destination.iata, destination.name)

            flight = Flight(
                trip=trip,
                carrier_id=db.query(Airline.id)
                    .filter(Airline.iata == flight_tag.find("Carrier").get('id')).first()[0],
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
            db.add(flight)

        return trip

    def process_itinerary(self, tag):
        onward_tag = tag.find('OnwardPricedItinerary')
        return_tag = tag.find('ReturnPricedItinerary')

        itinerary = Itinerary(request=self.request)
        itinerary.onward_trip = self.process_trip(onward_tag)
        itinerary.return_trip = None if return_tag is None else self.process_trip(return_tag)

        price_details = []
        pricing_tag = tag.find('Pricing')
        for charge_tag in pricing_tag.findall('ServiceCharges'):
            data = {
                'currency': pricing_tag.get('currency'),
                'type': charge_tag.get('type'),
                'charge_type': charge_tag.get('ChargeType'),
                'amount': Decimal(charge_tag.text)
            }
            if data['charge_type'] == 'TotalAmount':
                if data['type'] == 'SingleAdult':
                    itinerary.price_adult = data['amount']
                elif data['type'] == 'SingleChild':
                    itinerary.price_child = data['amount']
                elif data['type'] == 'SingleInfant':
                    itinerary.price_infant = data['amount']

            price_details.append(data)

        itinerary.price_details = price_details

        db.add(itinerary)
        return itinerary


    def run(self):
        tree = etree.parse(self.stream)

        self.request = SearchRequest(
            partner_request_id=tree.getroot().find('RequestId').text,
            partner_tag=self.partner_tag,
        )

        db.add(self.request)

        for flights_tag in tree.getroot().findall('PricedItineraries/Flights'):
            itinerary = self.process_itinerary(flights_tag)

        db.commit()
