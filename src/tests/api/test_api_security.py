import logging
from operator import attrgetter

import authorization_levels
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
        'in_onderzoek',
        'beschrijving_monument',
        'redengevende_omschrijving_monument',
        'beschrijving_complex',
    ]

    NON_OPENFIELDS_MONUMENT = [
        'architect_ontwerp_monument',
        'monumenttype',
        'opdrachtgever_bouw_monument',
        'bouwjaar_start_bouwperiode_monument',
        'bouwjaar_eind_bouwperiode_monument',
        'oorspronkelijke_functie_monument',
        'monumentgeometrie',
    ]

    OPENFIELDS_COMPLEX = [
        'identificerende_sleutel_complex',
        'monumentnummer_complex',
        'complexnaam',
        'beschrijving_complex',
    ]

    NON_OPENFIELDS_COMPLEX = [
    ]

    HALF_OPEN_FIELDS_MONUMENT = {
        'redengevende_omschrijving_monument': 'redengevende_omschrijving_monument_publiek',
        'beschrijving_complex': 'complex.beschrijving_complex_publiek',
        'beschrijving_monument': 'beschrijving_monument_publiek',
    }

    HALF_OPEN_FIELDS_COMPLEX = {
        'beschrijving_complex': 'beschrijving_complex_publiek',
    }

    def setUp(self):
        create_testset()

    def test_security_monumenten(self):
        monument0 = models.Monument.objects.all()[0]
        url = '/monumenten/monumenten/{}/'.format(
            monument0.id)

        self.client.credentials()
        fields_visible_by_public = self.client.get(url).data

        credentials = self.employee_credentials(authorization_levels.SCOPE_MON_RDM)
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

            if f in self.HALF_OPEN_FIELDS_MONUMENT.keys():
                if attrgetter(self.HALF_OPEN_FIELDS_MONUMENT[f])(monument0):
                    self.assertTrue(
                        f in fields_visible_by_public,
                        'Field should be visible by public: {}'.format(f))
                else:
                    self.assertTrue(
                        f not in fields_visible_by_public,
                        'Field should be visible by public: {}'.format(f))

    def test_security_complexen(self):
        complex0 = models.Complex.objects.all()[0]
        url = '/monumenten/complexen/{}/'.format(
            complex0.id)

        self.client.credentials()
        fields_visible_by_public = self.client.get(url).data

        credentials = self.employee_credentials(authorization_levels.SCOPE_MON_RBC)
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

            if f in self.HALF_OPEN_FIELDS_COMPLEX.keys():
                if attrgetter(self.HALF_OPEN_FIELDS_COMPLEX[f])(complex0):
                    self.assertTrue(
                        f in fields_visible_by_public,
                        'Field should be visible by public: {}'.format(f))
                else:
                    self.assertTrue(
                        f not in fields_visible_by_public,
                        'Field should be visible by public: {}'.format(f))
