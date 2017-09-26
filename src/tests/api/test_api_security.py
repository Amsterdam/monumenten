import logging

from rest_framework.test import APITestCase
from monumenten.dataset import models

from .factories import create_testset
from .mixins import JWTMixin

log = logging.getLogger(__name__)


class TestAPIEndpoints(JWTMixin, APITestCase):
    """
    Verifies that security in the API works correctly.
    """

    OPENFIELDS_MONUMENT = [
        'identificerende_sleutel_monument',
        'monumentnummer',
        'monumentnaam',
        'monumentstatus',
        'monument_aanwijzingsdatum',
        'betreft_pand',
        '_display',
        'heeft_als_grondslag_beperking',
        'heeft_situeringen',
        'monumentcoordinaten',
    ]

    NON_OPENFIELDS_MONUMENT = [
        'architect_ontwerp_monument',
        'monumenttype',
        'opdrachtgever_bouw_monument',
        'bouwjaar_start_bouwperiode_monument',
        'bouwjaar_eind_bouwperiode_monument',
        'oorspronkelijke_functie_monument',
        'monumentgeometrie',
        'in_onderzoek',
        'beschrijving_monument',
        'redengevende_omschrijving_monument',
        'beschrijving_complex',
    ]

    OPENFIELDS_COMPLEX = [
        'identificerende_sleutel_complex',
        'monumentnummer_complex',
        'complexnaam',
    ]

    NON_OPENFIELDS_COMPLEX = [
        'beschrijving_complex',
    ]

    def setUp(self):
        create_testset()

    def test_security_monumenten(self):
        url = '/monumenten/monumenten/{}/'.format(
            models.Monument.objects.all()[0].id)

        self.client.credentials()
        fields_visible_by_public = self.client.get(url).data

        for scope in (None, "MON/RC"):
            credentials = self.employee_credentials(scope=scope)
            log.debug(credentials)
            self.client.credentials(**credentials)
            fields_visible_by_employee = self.client.get(url).data

            for f in self.NON_OPENFIELDS_MONUMENT:
                self.assertTrue(
                    f in fields_visible_by_employee,
                    'Field should be visible by employee: {}'.format(f))
                self.assertTrue(
                    f not in fields_visible_by_public,
                    'Field should NOT be visible by public: {}'.format(f))

            for f in self.OPENFIELDS_MONUMENT:
                self.assertTrue(
                    f in fields_visible_by_employee,
                    'Field should be visible by employee: {}'.format(f))
                self.assertTrue(
                    f in fields_visible_by_public,
                    'Field should be visible by public: {}'.format(f))

    def test_security_complexen(self):
        url = '/monumenten/complexen/{}/'.format(
            models.Complex.objects.all()[0].id)

        self.client.credentials()
        fields_visible_by_public = self.client.get(url).data

        for scope in (None, "MON/RC"):
            credentials = self.employee_credentials(scope=scope)
            log.debug(credentials)
            self.client.credentials(**credentials)
            fields_visible_by_employee = self.client.get(url).data

            for f in self.NON_OPENFIELDS_COMPLEX:
                self.assertTrue(
                    f in fields_visible_by_employee,
                    'Field should be visible by employee: {}'.format(f))
                self.assertTrue(
                    f not in fields_visible_by_public,
                    'Field should NOT be visible by public: {}'.format(f))

            for f in self.OPENFIELDS_COMPLEX:
                self.assertTrue(
                    f in fields_visible_by_employee,
                    'Field should be visible by employee: {}'.format(f))
                self.assertTrue(
                    f in fields_visible_by_public,
                    'Field should be visible by public: {}'.format(f))
