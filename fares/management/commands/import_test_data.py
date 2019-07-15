import os

from django.core.management import BaseCommand

from fares.data_import.xml_importer import XmlImporter


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open(os.path.join('data', 'RS_Via-3.xml'), 'rt') as f:
            importer = XmlImporter(f, "3")
            importer.run()

        with open(os.path.join('data', 'RS_ViaOW.xml'), 'rt') as f:
            importer = XmlImporter(f, "OW")
            importer.run()
