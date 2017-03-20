import logging

from rest_framework.test import APITestCase
from monumenten.dataset import models

from .factories import create_testset
from .mixins import JWTMixin

log = logging.getLogger(__name__)


class TestAPIEndpoints(JWTMixin,APITestCase):
    """
    Verifies that security in the API works correctly.
    """

    OPENFIELDS = ['id',
                      'monumentnummer',
                      'monumentnaam',
                      'monumentstatus',
                      'monument_aanwijzingsdatum',
                      'betreft_pand',
                      'display_naam',
                      'complex_id',
                      'complex_naam',
                      'complex_monumentnummer',
                      'heeft_als_grondslag_beperking',
                      'heeft_situeringen',
                      'monumentcoordinaten',
                      'afbeelding',
                      ]

    NON_OPENFIELDS = ['architect_ontwerp_monument',
                          'monumenttype',
                          'opdrachtgever_bouw_monument',
                          'bouwjaar_start_bouwperiode_monument',
                          'bouwjaar_eind_bouwperiode_monument',
                          'oorspronkelijke_functie_monument',
                          'monumentgeometrie',
                          'in_onderzoek',
                          'beschrijving_monument',
                          'redengevende_omschrijving_monument',
                          'complex_beschrijving',]

    def setUp(self):
        create_testset()

    def test_security(self):
        url = '/monumenten/monumenten/{}/'.format(models.Monument.objects.all()[0].id)

        self.client.credentials()
        fields_visible_by_public = self.client.get(url).data

        self.client.credentials(**self.employee_credentials())
        fields_visible_by_employee = self.client.get(url).data

        for f in self.NON_OPENFIELDS:
            self.assertTrue(f in fields_visible_by_employee, 'Field should be visible by employee: {}'.format(f))
            self.assertTrue(f not in fields_visible_by_public, 'Field should NOT be visible by public: {}'.format(f))

        for f in self.OPENFIELDS:
            self.assertTrue(f in fields_visible_by_employee, 'Field should be visible by employee: {}'.format(f))
            self.assertTrue(f in fields_visible_by_public, 'Field should be visible by public: {}'.format(f))

