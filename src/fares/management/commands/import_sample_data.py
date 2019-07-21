import os

from django.core.management import BaseCommand

from fares.data_import.xml_importer import XmlImporter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('rootdir', nargs=1, type=str)

    def handle(self, *args, **options):
        with open(os.path.join(options['rootdir'][0], 'RS_Via-3.xml'), 'rt') as f:
            importer = XmlImporter(f, "3")
            importer.run()

        with open(os.path.join(options['rootdir'][0], 'RS_ViaOW.xml'), 'rt') as f:
            importer = XmlImporter(f, "OW")
            importer.run()
