import logging

from django.core.management import BaseCommand

from monumenten.importer import xml_importer
from monumenten.objectstore import objectstore
log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run import.")
        for file_name in objectstore.fetch_import_file_names():
            local_file = objectstore.copy_file_from_objectstore(file_name)
            xml_importer.import_file(local_file)
