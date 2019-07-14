from django.core.management import BaseCommand

from fares.data_import.reference_import import import_airports, import_airlines


class Command(BaseCommand):

    def handle(self, *args, **options):
        import_airports()
        import_airlines()
