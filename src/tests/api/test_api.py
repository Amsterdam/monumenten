import logging

from rest_framework.test import APITestCase

from .factories import create_testset

log = logging.getLogger(__name__)


class TestAPIEndpoints(APITestCase):
    """
    Verifies that browsing the API works correctly.
    """

    reverse_list_urls = [
        ('health', None),
        ('situeringen', [60])
    ]
    detail_urls = [
        ('monumenten', (('', 200),
                        ('?pand_sleutel=10', 200),
                        ('?pand_sleutel=192048', 200),
                        ('?pand_sleutel=bla', 200),
                        ('?nietbestaand=bla', 200),
                        ('5/', 200))),
        ('situeringen', (('42/', 200),
                         ('?monument_id=23', 200),
                         ('?monument_id=nietbestaand', 200)
                         )),
    ]

    def setUp(self):
        # builds 10 complexes with 1 to 10 monuments and 1 to 10 situeringen
        create_testset()

    def valid_response(self, url, response, ret_code):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            ret_code, response.status_code,
            'Expected response code {} '
            'received {} for {}'.format(ret_code,
                                        response.status_code,
                                        url))

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def valid_html_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'text/html; charset=utf-8', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_details(self):
        for url, arguments in self.detail_urls:
            for args, ret_code in arguments:
                get_url = '/monumenten/{}/{}'.format(url, args)
                log.debug(
                    "test {}".format(get_url))
                response = self.client.get(get_url)
                self.valid_response(url, response, ret_code)
