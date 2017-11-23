import logging

from django.core.management import BaseCommand

from monumenten.importer import xml_importer
from monumenten.objectstore import objectstore
from monumenten.dataset.monumenten.batch import DeleteMonumentenIndexTask, IndexMonumentenTask, IndexComplexenTask

log = logging.getLogger(__name__)


class Command(BaseCommand):

    indexes = dict(
        monumenten=[DeleteMonumentenIndexTask, IndexMonumentenTask, IndexComplexenTask],
    )

    def add_arguments(self, parser):
        parser.add_argument('--no-import',
                            action='store_false',
                            dest='run-import',
                            default=True,
                            help='Skip database importing')

        parser.add_argument('--no-index',
                            action='store_false',
                            dest='run-index',
                            default=True,
                            help='Skip elastic search indexing')

    def handle(self, *args, **options):
        if options['run-import']:
            self.stdout.write("Run import.")
            for file_name in objectstore.fetch_import_file_names():
                local_file = objectstore.copy_file_from_objectstore(file_name)
                xml_importer.import_file(local_file)

        if options['run-index']:
            for job_class in self.indexes['monumenten']:
                job_class().execute()
