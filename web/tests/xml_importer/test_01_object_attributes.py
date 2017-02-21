from unittest import TestCase
from monumenten.importer.xml_importer import import_file
import xmltodict

from monumenten.dataset.models import Monument
from datetime import date

class TestObjectStore(TestCase):
    """
    https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:monumenten:start
    vragen:
    1) de tags "Architect, Opdrachtgever, PeriodeStart, PeriodeEind, Functie" staan nog niet in de xml, is dat bewust gedaan?
    2) Tekst[Type=Omschrijving] kent meerdere statussen. Moet alleen de omschrijving met status "Afgerond" meegenomen worden?
    3) Tekst[Type=Redengevende beschrijving] kent meerdere statussen. Moet alleen de beschrijving met status "Vastgesteld" meegenomen worden?
    4) Is het attribuut 'Notitie' nog nodig in de de database, of valt deze onder 'Omschrijving' of 'Redengevende beschrijving'?
    5) Is het attribuut 'Beschrijving complex' nog nodig in de database? Immers: deze kan opgevraagd worden met behulp van 'Complex nummer'.
    6) Is er een aparte tabel nodig voor 'Complex' objects? Kunnen deze ook opgeslagen worden in de Monumenten tabel met Type='Complex'?
    7) Een aantal objecten hebben een MULTIPOLYGON. Hoe hiermee om te gaan?
    """

    def test_import(self):

        import_file(filename='tests/files/01_object_attributes.xml')
        #import_file(filename='/Users/patrickberkhout/Downloads/AMISExport.xml')

        monument = Monument.objects.get(id='d5cc6402-d211-4981-b965-08a559837218')

        # Monumentnummer
        self.assertEqual(monument.monumentnummer, 123456, 'Monumentnummer')

        # Monumentnaam
        self.assertEqual(monument.naam, None, 'Naam')

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
        self.assertEqual(str(monument.punt), 'SRID=28992;POINT (123456 123456)', 'Punt')

        # Monumentgeometrie
        self.assertEqual(str(monument.polygoon)[:30], 'SRID=28992;POLYGON ((116488.01', 'Polygoon')

        # Beperking
        self.assertEqual(monument.beperking, None, 'Beperking')

        # In onderzoek
        self.assertEqual(monument.beperking, None, 'In Onderzoek')

        # Beschrijving monument
        self.assertEqual(str(monument.beschrijving)[:30], 'NOTITIE1', 'Beschrijving')

        # Redengevende omschrijving monument
        self.assertEqual(str(monument.redengevende_omschrijving)[:30], 'Notitie 2', 'Redengevende omschrijving')

        # Foto van monument
        self.assertEqual(monument.afbeelding, '27eb9135-b68e-4a51-b197-3a3299fb5dbc', 'Afbeelding')

        # Notitie
        #  ???

        # Complex nummer
        self.assertEqual(monument.complex_nummer, 518301, 'Complex nummer')

        # Complex naam
        self.assertEqual(monument.complex_naam, 'Naam199', 'Complex naam')

        # Adressen
        # TODO

        # Identificerende sleutel monument
        self.assertEqual(monument.id, 'd5cc6402-d211-4981-b965-08a559837218', 'Id')

        # Identificerende sleutel complex
        self.assertEqual(monument.complex_id, '9d278d0d-c5c0-4c8d-9f4e-081d7706b42e', 'Complex Id')

        # Identificerende sleutel situering
        # TODO
