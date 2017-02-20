from unittest import TestCase
from monumenten.importer.xml_importer import import_file
import xmltodict

from monumenten.dataset.models import Monument

class TestObjectStore(TestCase):

    def test_os_connect(self):

        print(Monument.objects.all())
        import_file(filename='tests/files/file01.xml')

        print(Monument.objects.all())


