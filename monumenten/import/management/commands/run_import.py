import sys
import logging

from django.core.management import BaseCommand, call_command

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass


    def handle(self, *args, **options):
        self.stdout.write("Run import.")
