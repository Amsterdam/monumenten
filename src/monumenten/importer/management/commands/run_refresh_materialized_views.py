import logging

from django.core.management import BaseCommand

from monumenten.importer import refresh_materialized_views

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run refresh materialized views")

        refresh_materialized_views.refresh_geo_monument_point()

