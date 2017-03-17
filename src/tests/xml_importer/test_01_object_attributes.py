from datetime import date
from unittest import TestCase

from monumenten.dataset.models import Monument, Complex
from monumenten.importer.xml_importer import import_file


class TestObjectStore(TestCase):
    """
    https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:monumenten:start
    vragen:
    1) de tags "Architect, Opdrachtgever, PeriodeStart, PeriodeEind, Functie" staan nog niet in de xml, is dat bewust gedaan?
        --> vraag staat nog uit.
    """

    def test_import(self):

        import_file(filename='tests/files/01_object_attributes.xml')

        monument = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837218')
        monument_2 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837219')
        monument_3 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837220')
        monument_4 = Monument.objects.get(external_id='d5cc6402-d211-4981-b965-08a559837221')
        complex = Complex.objects.get(external_id='9d278d0d-c5c0-4c8d-9f4e-081d7706b42e')

        # Monumentnummer
        self.assertEqual(monument.monumentnummer, 123456, 'Monumentnummer')
        self.assertEqual(monument_3.monumentnummer, None, 'Monumentnummer')

        # Monumentnaam
        self.assertEqual(monument.monumentnaam, 'Monumentje', 'Naam')
        self.assertEqual(monument_3.monumentnaam, None, 'Naam')

        self.assertEqual(monument.display_naam, 'Monumentje', 'Naam')
        self.assertEqual(monument_2.display_naam, 'Straatje2 50 H', 'Naam')
        self.assertEqual(monument_4.display_naam, 'Straatje4 50 A H', 'Naam')

        # Monumenttype
        self.assertEqual(monument.monumenttype, 'Pand', 'Type')

        # Monumentstatus
        self.assertEqual(monument.monumentstatus, 'Status100', 'Status mismatch')

        # Architect ontwerp monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.architect_ontwerp_monument, None, 'Architect')

        # Monument aanwijzingsdatum
        self.assertEqual(monument.monument_aanwijzingsdatum, date(2015, 1, 9), 'Aanwijzingsdatum')

        # Heeft als grondslag -- leeg, want staat niet in xml
        self.assertEqual(monument.heeft_als_grondslag_beperking, None, 'Heeft als grondslag')

        # Opdrachtgever bouw monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.opdrachtgever_bouw_monument, None, 'Opdrachtgever')

        # Bouwjaar start bouwperiode monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.bouwjaar_start_bouwperiode_monument, None, 'Periode start')

        # Bouwjaar eind bouwperiode monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.bouwjaar_eind_bouwperiode_monument, None, 'Periode eind')

        # Oorspronkelijke functie monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.oorspronkelijke_functie_monument, None, 'Functie')

        # Betreft (BAG verwijzing - Pand)
        self.assertEqual(monument.betreft_pand, '0363' + '10' + '0013072812',
                         'Pand Sleutel')

        # Monumentcoördinaten
        self.assertEqual(str(monument.monumentcoordinaten), 'SRID=28992;POINT (123456 123456)', 'Coordinaten')

        # Monumentgeometrie
        self.assertEqual(str(monument.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POLYGON ((116488.01', 'Geometrie')
        self.assertEqual(str(monument_2.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (MULTIPOLYGON (((126', 'Geometrie')
        self.assertEqual(str(monument_3.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POINT (121498.47019', 'Geometrie')
        self.assertEqual(str(monument_4.monumentgeometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (LINESTRING (121556.', 'Geometrie')

        # Beperking
        self.assertEqual(monument.beperking, None, 'Beperking')

        # In onderzoek
        self.assertEqual(monument.in_onderzoek, 'Ja', 'In Onderzoek')
        self.assertEqual(monument_2.in_onderzoek, 'Ja', 'In Onderzoek')

        # Beschrijving monument
        # Tekst/Type='Beschrijving'/Status='Afgerond'/Notitie
        self.assertEqual(str(monument.beschrijving_monument)[:30], 'NOTITIE1', 'Beschrijving')

        # Redengevende omschrijving monument
        # Tekst/Type='Redengevende omschrijving'/Status='Vastgesteld'/Notitie
        self.assertEqual(str(monument.redengevende_omschrijving_monument)[:30], 'Notitie 2', 'Redengevende omschrijving')

        # Foto van monument
        self.assertEqual(monument.afbeelding, '27eb9135-b68e-4a51-b197-3a3299fb5dbc', 'Afbeelding')

        # Adressen
        adresses = sorted(list(monument.situeringen.all()), key=lambda s: s.external_id)
        self.assertEqual(adresses[0].external_id, '2f4546b5-7528-443b-9474-ef3c31a2f018', 'Adres id')
        self.assertEqual(adresses[0].betreft_nummeraanduiding, '0363' + '20' + '0000177987',
                         'Adres betreft = BAG sleutel')
        self.assertEqual(adresses[0].situering_nummeraanduiding, 'Conversie', 'Adres situering')
        self.assertEqual(adresses[0].eerste_situering, 'Ja', 'Adres eerste_situering')
        self.assertEqual(adresses[0].huisletter, 'A', 'Adres huisletter')
        self.assertEqual(adresses[0].huisnummer, 52, 'Adres huisnummer')
        self.assertEqual(adresses[0].huisnummertoevoeging, '3', 'Adres huisnummertoevoeging')
        self.assertEqual(adresses[0].postcode, '1000AA', 'Adres postcode')
        self.assertEqual(adresses[0].straat, 'Straatje', 'Adres straat')

        # Identificerende sleutel monument
        self.assertIsNotNone(monument.id, 'Id')

        # Identificerende sleutel complex
        self.assertIsNotNone(monument.id, 'Complex Id')

        # Identificerende sleutel situering
        adresses = sorted(list(monument.situeringen.all()), key=lambda s: s.id)
        self.assertIsNotNone(adresses[0].id, 'Adres id')

        # Identificerende sleutel complex complex
        self.assertIsNotNone(complex.id, 'Complex id')

        # Monumentnummer complex
        self.assertEqual(complex.monumentnummer, 518301, 'Complex nummer')

        # Complexnaam
        self.assertEqual(complex.complex_naam, 'Complex1999', 'Complex naam')

        # Beschrijving complex
        self.assertEqual(complex.beschrijving, 'Notitie4', 'Complex beschrijving')

        # Status complex - NOOT: staat niet in stelselpedia
        self.assertEqual(complex.complexstatus, 'Rijksmonument', 'Complex status')
