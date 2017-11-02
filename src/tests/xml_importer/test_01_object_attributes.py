from datetime import date
from unittest import TestCase
from rest_framework.test import APITestCase

from monumenten.dataset.models import Monument, Complex
from monumenten.dataset.monumenten.batch import DeleteMonumentenIndexTask, IndexMonumentenTask, IndexComplexenTask
from monumenten.importer.xml_importer import import_file


def do_import():
    import_file(filename='tests/files/01_object_attributes.xml')
    monument_1 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837218')
    monument_2 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837219')
    monument_3 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837220')
    monument_4 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837221')
    complex_1 = Complex.objects.get(external_id='9d278d0d-c5c0-4c8d-9f4e-081d7706b42e')
    return (monument_1, monument_2, monument_3, monument_4, complex_1)


class TestObjectStore(TestCase):
    """
    zie https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:monumenten:databestanden
    voor openstaande vragen
    """

    def test_import(self):
        (monument_1, monument_2, monument_3, monument_4, complex_1) = do_import()

        # Monumentnummer
        self.assertEqual(monument_1.monumentnummer, 123456, 'Monumentnummer')
        self.assertEqual(monument_3.monumentnummer, None, 'Monumentnummer')

        # Monumentnaam
        self.assertEqual(monument_1.monumentnaam, 'Monumentje', 'Naam')
        self.assertEqual(monument_3.monumentnaam, None, 'Naam')

        self.assertEqual(monument_1.display_naam, 'Monumentje', 'Naam')
        self.assertEqual(monument_2.display_naam, 'Straatje2 50 H', 'Naam')
        self.assertEqual(monument_4.display_naam, 'Straatje4 50 A H', 'Naam')

        # Monumenttype
        self.assertEqual(monument_1.monumenttype, 'Pand', 'Type')

        # Monumentstatus
        self.assertEqual(monument_1.monumentstatus, 'Status100', 'Status mismatch')

        # Architect ontwerp monument_1 -- leeg want nog niet gevuld in xml
        self.assertEqual(monument_1.architect_ontwerp_monument, 'Architectje', 'Architect')

        # Monument aanwijzingsdatum
        self.assertEqual(monument_1.monument_aanwijzingsdatum, date(2015, 1, 9), 'Aanwijzingsdatum')

        # Heeft als grondslag - wordt niet geleverd
        self.assertEqual(monument_1.heeft_als_grondslag_beperking, None, 'Heeft als grondslag')

        # Opdrachtgever bouw monument_1
        self.assertEqual(monument_1.opdrachtgever_bouw_monument, 'Jan', 'Opdrachtgever')

        # Bouwjaar start bouwperiode monument_1
        self.assertEqual(monument_1.bouwjaar_start_bouwperiode_monument, 1898, 'Periode start')

        # Bouwjaar eind bouwperiode monument_1
        self.assertEqual(monument_1.bouwjaar_eind_bouwperiode_monument, 1900, 'Periode eind')

        # Oorspronkelijke functie monument_1
        self.assertEqual(monument_1.oorspronkelijke_functie_monument, 'Gebouwen, woonhuizen', 'Functie')
        self.assertEqual(monument_2.oorspronkelijke_functie_monument, None, 'Functie')

        # Betreft (BAG verwijzing - Pand)
        self.assertEqual(monument_1.betreft_pand, '0' + '3630013072812',
                         'Pand Sleutel')

        # Monumentcoördinaten
        self.assertEqual(str(monument_1.monumentcoordinaten), 'SRID=28992;POINT (123456 123456)', 'Coordinaten')

        # Monumentgeometrie
        self.assertEqual(str(monument_1.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POLYGON ((116488.01', 'Geometrie')
        self.assertEqual(str(monument_2.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (MULTIPOLYGON (((126', 'Geometrie')
        self.assertEqual(str(monument_3.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POINT (121498.47019', 'Geometrie')
        self.assertEqual(str(monument_4.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (LINESTRING (121556.', 'Geometrie')

        # In onderzoek
        self.assertEqual(monument_1.in_onderzoek, 'J', 'In Onderzoek')
        self.assertEqual(monument_2.in_onderzoek, 'J', 'In Onderzoek')

        # Beschrijving monument_1
        # Tekst/Type='Beschrijving'/Status='Afgerond'/Notitie
        self.assertEqual(str(monument_1.beschrijving_monument)[:30], 'NOTITIE1', 'Beschrijving')

        # Redengevende omschrijving monument_1
        # Tekst/Type='Redengevende omschrijving'/Status='Vastgesteld'/Notitie
        self.assertEqual(str(monument_1.redengevende_omschrijving_monument)[:30], 'Notitie 2', 'Redengevende omschrijving')

        # Foto van monument_1
        self.assertEqual(monument_1.afbeelding, '27eb9135-b68e-4a51-b197-3a3299fb5dbc', 'Afbeelding')

        # Adressen
        adresses = sorted(list(monument_1.situeringen.all()), key=lambda s: s.external_id)
        self.assertEqual(adresses[0].external_id, '2f4546b5-7528-443b-9474-ef3c31a2f018', 'Adres id')
        self.assertEqual(adresses[0].betreft_nummeraanduiding, '0'+ '3630000177987',
                         'Adres betreft = BAG sleutel')
        self.assertEqual(adresses[0].situering_nummeraanduiding, 'Actueel', 'Adres situering')
        self.assertEqual(adresses[0].eerste_situering, 'J', 'Adres eerste_situering')
        self.assertEqual(adresses[0].huisletter, 'A', 'Adres huisletter')
        self.assertEqual(adresses[0].huisnummer, 52, 'Adres huisnummer')
        self.assertEqual(adresses[0].huisnummertoevoeging, '3', 'Adres huisnummertoevoeging')
        self.assertEqual(adresses[0].postcode, '1000AA', 'Adres postcode')
        self.assertEqual(adresses[0].straat, 'Straatje', 'Adres straat')

        # Identificerende sleutel monument_1
        self.assertIsNotNone(monument_1.id, 'Id')
        self.assertEqual('d5cc6402-d211-4981-b965-08a559837218', monument_1.id, 'Id')

        # Identificerende sleutel complex_1
        self.assertIsNotNone(complex_1.id, 'Complex Id')
        self.assertEqual(
            '9d278d0d-c5c0-4c8d-9f4e-081d7706b42e', complex_1.id, 'Id')

        # Identificerende sleutel situering
        adresses = sorted(list(monument_1.situeringen.all()), key=lambda s: s.id)
        self.assertIsNotNone(adresses[0].id, 'Adres id')

        # Identificerende sleutel complex_1 complex_1
        self.assertIsNotNone(complex_1.id, 'Complex id')

        # Monumentnummer complex_1
        self.assertEqual(complex_1.monumentnummer_complex, 518301, 'Complex nummer')

        # Complexnaam
        self.assertEqual(complex_1.complexnaam, 'Complex1999', 'Complex naam')

        # Beschrijving complex_1
        self.assertEqual(complex_1.beschrijving_complex, 'Notitie4', 'Complex beschrijving')

        # Status complex_1 - NOOT: staat niet in stelselpedia
        self.assertEqual(complex_1.complexstatus, 'Rijksmonument', 'Complex status')

class TestSearch(APITestCase):
    def test_search(self):
        """
        test search
        """
        do_import()

        for job_class in [DeleteMonumentenIndexTask, IndexMonumentenTask, IndexComplexenTask]:
            job_class().execute()

        search_endpoint = '/monumenten/search/'
        query = 'complex1999'

        response = self.client.get(search_endpoint, {'q': "".join(query)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['count'] > 0)
        self.assertEqual(response.data['results'][0]['type'], 'complex')
        self.assertEqual(response.data['results'][0]['complexnaam'], 'Complex1999')
        self.assertEqual(response.data['results'][0]['_links']['self']['href'],
                         'http://testserver/monumenten/complexen/9d278d0d-c5c0-4c8d-9f4e-081d7706b42e/')

    def test_typeahead(self):
        """
        test search
        """
        search_endpoint = '/monumenten/typeahead/'
        query = 'monumentje'

        response = self.client.get(search_endpoint, {'q': "".join(query)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['content'][0]['display_naam'], 'Monumentje')
        self.assertEqual(response.data[0]['content'][0]['uri'], 'monumenten/monumenten/d5cc6402-d211-4981-b965-08a559837218')

        query = 'complex1999'
        response = self.client.get(search_endpoint, {'q': "".join(query)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['content'][0]['complexnaam'], 'Complex1999 (complex)')


