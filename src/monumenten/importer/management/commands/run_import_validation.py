import logging

from django.core.management import BaseCommand

from monumenten.importer import xml_importer, import_validation
from monumenten.objectstore import objectstore
log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run import validation.")
        import_validation.check_import()