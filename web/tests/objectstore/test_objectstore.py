from unittest import TestCase


from monumenten.objectstore import objectstore
import os

class TestObjectStore(TestCase):

    def test_os_connect(self):
        assert objectstore.os_connect['tenant_name'] == 'BGE000081_Cultuur'

    def test_fetch_import_file_names(self):
        file_names = objectstore.fetch_import_file_names()
        print(file_names)
        self.assertTrue((len(file_names) > 0), "1 more 1 files should be found")
