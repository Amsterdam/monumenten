import logging
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .factories import create_testset

log = logging.getLogger(__name__)


class TestAPIEndpoints(APITestCase):
    """
    Verifies that browsing the API works correctly.
    """

    reverse_list_urls = [
        # 'docs',
        ('monumenten-list', None),
        # ('situering-list', [10])
    ]
    reverse_detail_urls = [
        'monumenten-detail',
        'situering-detail',
    ]

    def setUp(self):
        create_testset()            # builds 10 complexex with 1 to 10 monuments and 1 to 10 situeringen

    def valid_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

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

    def test_lists(self):
        for url, arguments in self.reverse_list_urls:
            log.debug("test {} => {}".format(url, reverse(url, arguments)))
            response = self.client.get(reverse(url, arguments))
            self.valid_response(url, response)
            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(
                response.data['count'],
                0, 'Wrong result count for {}'.format(url))

    # def test_details(self):
    #     for url in self.reverse_detail_urls:
    #         log.debug("test {} => {}".format(url, reverse(url, [1])))
    #         self.valid_response(url, self.client.get(reverse(url, [1])))
