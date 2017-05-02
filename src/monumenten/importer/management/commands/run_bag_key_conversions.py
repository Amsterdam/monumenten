import logging

from django.core.management import BaseCommand

from monumenten.importer import bag_key_conversions

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run bag key conversions.")

        bag_key_conversions.update_landelijk_id_nummeraanduiding()

        bag_key_conversions.update_landelijk_id_pand()
