from django.core.management import BaseCommand

from fares.data_import.reference_import import import_airports, import_airlines


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('rootdir', nargs=1, type=str)

    def handle(self, *args, **options):
        import_airports(options['rootdir'][0])
        import_airlines(options['rootdir'][0])
