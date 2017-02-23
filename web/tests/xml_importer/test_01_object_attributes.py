from unittest import TestCase
from monumenten.importer.xml_importer import import_file
import xmltodict

from monumenten.dataset.models import Monument, Complex
from datetime import date

class TestObjectStore(TestCase):
    """
    https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:monumenten:start
    vragen:
    1) de tags "Architect, Opdrachtgever, PeriodeStart, PeriodeEind, Functie" staan nog niet in de xml, is dat bewust gedaan?
        --> vraag staat nog uit.
    """

    def test_import(self):

        import_file(filename='tests/files/01_object_attributes.xml')
        #import_file(filename='/Users/patrickberkhout/Downloads/AMISExport.xml')

        monument = Monument.objects.get(id='d5cc6402-d211-4981-b965-08a559837218')
        monument_2 = Monument.objects.get(id='d5cc6402-d211-4981-b965-08a559837219')
        monument_3 = Monument.objects.get(id='d5cc6402-d211-4981-b965-08a559837220')
        monument_4 = Monument.objects.get(id='d5cc6402-d211-4981-b965-08a559837221')
        complex = Complex.objects.get(id='9d278d0d-c5c0-4c8d-9f4e-081d7706b42e')

        # Monumentnummer
        self.assertEqual(monument.monumentnummer, 123456, 'Monumentnummer')
        self.assertEqual(monument_3.monumentnummer, None, 'Monumentnummer')

        # Monumentnaam
        self.assertEqual(monument.naam, 'Monumentje', 'Naam')
        self.assertEqual(monument_3.naam, None, 'Naam')

        # Monumenttype
        self.assertEqual(monument.type, 'Pand', 'Type')

        # Monumentstatus
        self.assertEqual(monument.status, 'Status100', 'Status mismatch')

        # Architect ontwerp monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.architect, None, 'Architect')

        # Monument aanwijzingsdatum
        self.assertEqual(monument.aanwijzingsdatum, date(2015, 1, 9), 'Aanwijzingsdatum')

        # Opdrachtgever bouw monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.opdrachtgever, None, 'Opdrachtgever')

        # Bouwjaar start bouwperiode monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.periode_start, None, 'Periode start')

        # Bouwjaar eind bouwperiode monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.periode_eind, None, 'Periode eind')

        # Oorspronkelijke functie monument -- leeg want nog niet gevuld in xml
        self.assertEqual(monument.functie, None, 'Functie')

        # Pand
        self.assertEqual(monument.pand_sleutel, 3630013072812, 'Pand Sleutel')

        # Monumentcoördinaten
        self.assertEqual(str(monument.coordinaten), 'SRID=28992;POINT (123456 123456)', 'Coordinaten')

        # Monumentgeometrie
        self.assertEqual(str(monument.geometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POLYGON ((116488.01', 'Geometrie')
        self.assertEqual(str(monument_2.geometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (MULTIPOLYGON (((126', 'Geometrie')
        self.assertEqual(str(monument_3.geometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (POINT (121498.47019', 'Geometrie')
        self.assertEqual(str(monument_4.geometrie)[:50], 'SRID=28992;GEOMETRYCOLLECTION (LINESTRING (121556.', 'Geometrie')

        # Beperking
        self.assertEqual(monument.beperking, None, 'Beperking')

        # In onderzoek
        self.assertEqual(monument.in_onderzoek, 'Ja', 'In Onderzoek')
        self.assertEqual(monument_2.in_onderzoek, 'Ja', 'In Onderzoek')

        # Beschrijving monument
        # Tekst/Type='Beschrijving'/Status='Afgerond'/Notitie
        self.assertEqual(str(monument.beschrijving)[:30], 'NOTITIE1', 'Beschrijving')

        # Redengevende omschrijving monument
        # Tekst/Type='Redengevende omschrijving'/Status='Vastgesteld'/Notitie
        self.assertEqual(str(monument.redengevende_omschrijving)[:30], 'Notitie 2', 'Redengevende omschrijving')

        # Foto van monument
        self.assertEqual(monument.afbeelding, '27eb9135-b68e-4a51-b197-3a3299fb5dbc', 'Afbeelding')

        # Adressen
        # TODO

        # Identificerende sleutel monument
        self.assertEqual(monument.id, 'd5cc6402-d211-4981-b965-08a559837218', 'Id')

        # Identificerende sleutel complex
        self.assertEqual(monument.complex_id, '9d278d0d-c5c0-4c8d-9f4e-081d7706b42e', 'Complex Id')

        # Identificerende sleutel situering
        # TODO


        # Identificerende sleutel complex complex
        self.assertEqual(complex.id, '9d278d0d-c5c0-4c8d-9f4e-081d7706b42e', 'Complex Id')

        # Monumentnummer complex
        self.assertEqual(complex.monumentnummer, 518301, 'Complex nummer')

        # Complexnaam
        self.assertEqual(complex.naam, 'Complex1999', 'Complex naam')

        # Beschrijving complex
        self.assertEqual(complex.beschrijving, 'Notitie4', 'Complex beschrijving')

        # Status complex - NOOT: staat niet in stelselpedia
        self.assertEqual(complex.status, 'Rijksmonument', 'Complex status')
