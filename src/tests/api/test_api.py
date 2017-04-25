import logging

from rest_framework.test import APITestCase

from .factories import create_testset

log = logging.getLogger(__name__)


class TestAPIEndpoints(APITestCase):
    """
    Verifies that browsing the API works correctly.


    # point = Point(121944.32, 487722.88)
    #               52.37638, 4.90177
    """

    reverse_list_urls = [
        ('health', None),
        ('situeringen', [60])
    ]

    detail_urls = [

        ('monumenten', (
            ('', '>'),
            ('?betreft_pand=10', 1),
            ('?betreft_pand=192048', 0),
            ('?betreft_pand=bla', 0),
            ('?nietbestaand=bla', '>'),
            ('0-0/', 'nr=12'),
            ('?locatie=121944.32,487722.88,10', 50),
            ('?locatie=52.37638,4.90177,10', 50),
            # location far away should show up nothing
            ('?locatie=121144.32,487722.88,10', 0),
            ('?locatie=52.39638,4.90177,10', 0)
        )),

        ('situeringen', (
            ('2/', 'nr=7'),
            ('?monument_id=0-0', '>'),
            ('?monument_id=nietbestaand', 0)
        )),

        ('complexen', (
            ('', '3'),
            ('2/', 'nr=4'),
            ('?monumentnummer_complex=8392183', 10),
            ('?monumentnummer_complex=nietbestaand', 0)
        )),
    ]

    def setUp(self):
        # builds 10 complexes with
        # 1 to 10 monuments and 1 to 10 situeringen
        create_testset()

    def test_index_pages(self):
        url = 'monumenten'

        response = self.client.get('/{}/'.format(url))

        self.assertEqual(
            response.status_code,
            200, 'Wrong response code for {}'.format(url))

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
            self.assertEqual(
                response.data['count'],
                nr_of_rows,
                str(response.data))
        elif nr_of_rows == '>':
            self.assertTrue(
                response.data['count'] > 0,
                str(response.data))
        elif nr_of_rows.startswith('nr='):
            nr = int(nr_of_rows.split('=')[1])
            self.assertEqual(len(response.data), nr, str(response.data))

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
                log.debug("test %s", get_url)
                response = self.client.get(get_url)
                self.valid_response(url, response, nr_of_rows)
