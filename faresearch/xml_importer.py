
from typing import TextIO

from lxml import etree


class XmlImporter:
    def run(self, stream: TextIO):
        tree = etree.parse(stream)

        for flights_tag in tree.getroot().findall('.//Flights'):

            for itinerary_tag in flights_tag.findall('OnwardPricedItinerary'):
