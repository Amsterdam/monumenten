import logging

from django.core.management import BaseCommand

from monumenten.importer import add_missing_pand

log = logging.getLogger(__name__)


# this command should be run with a special version of manage_gevent.py that does the monkey patching right at the start
# Ie. python manage_gevent.py run_add_missing_pand
class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Run add missing pand")
        add_missing_pand.add_missing_pand()