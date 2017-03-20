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
        ('monumenten', (('', '>'),
                        ('?betreft_pand=10', 1),
                        ('?betreft_pand=192048', 0),
                        ('?betreft_pand=bla', 0),
                        ('?nietbestaand=bla', '>'),
                        ('5/', 'nr=13'))),
        ('situeringen', (('42/', 'nr=3'),
                         ('?monument_id=23', '>'),
                         ('?monument_id=nietbestaand', 0)
                         )),
    ]

    def setUp(self):
        # builds 10 complexes with 1 to 10 monuments and 1 to 10 situeringen
        create_testset()

    def valid_response(self, url, response, nr_of_rows):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Expected response code {} '
            'received {} for {}'.format(200,
                                        response.status_code,
                                        url))

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

        if isinstance((nr_of_rows), int):
            assert (response.data['count'] == nr_of_rows)
        elif nr_of_rows == '>':
            assert (response.data['count'] > 0)
        elif nr_of_rows.startswith('nr='):
            nr = int(nr_of_rows.split('=')[1])
            assert (len(response.data), nr)

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
            for args, nr_of_rows in arguments:
                get_url = '/monumenten/{}/{}'.format(url, args)
                log.debug(
                    "test {}".format(get_url))
                response = self.client.get(get_url)
                self.valid_response(url, response, nr_of_rows)
