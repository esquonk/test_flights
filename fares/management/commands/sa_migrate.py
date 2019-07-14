from django.core.management import BaseCommand

from db.models import create_all


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_all()

