# Python
import string
import random
# Packages
from rest_framework.test import APITestCase
# Project

import logging
log = logging.getLogger(__name__)


class RandomShitTest(APITestCase):

    def test_random_shit_typeahead(self):
        """
        random stuff that crashes search / inspired by ein smoke tests
        """

        typeahead_endpoints = [
            '/monumenten/typeahead/',
        ]

        for url in typeahead_endpoints:
            self.bomb_endpoint(url)

    def test_random_shit_search(self):
        """
        random stuff that crashes search / inspired by ein smoke tests
        """
        search_endpoints = [
            '/monumenten/search/',
        ]

        for url in search_endpoints:
            log.debug('random_testing: %s', url)
            self.bomb_endpoint(url)

    def bomb_endpoint(self, url):
        """
        Bomb enpoints with junk make sure nothing causes a
        crash
        """
        source = string.ascii_letters + string.digits + ' ' * 20
        for i in range(450):
            KEY_LEN = random.randint(1, 35)
            keylist = [random.choice(source) for i in range(KEY_LEN)]
            query = "".join(keylist)

            response = self.client.get(url, {
                'q': "".join(query)})

            self.assertEqual(response.status_code, 200)
