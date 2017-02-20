import logging

from django.core.management import BaseCommand
# from monumenten.importer import import_amis_xml
log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run import.")
