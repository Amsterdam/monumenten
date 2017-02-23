from django.contrib.gis.db import models


class Monument(models.Model):
    """
    Monument model
    NOTE: 'geometrie' type is GeometryCollectionField, possibly in future (e.g. for searching)
    this needs to be split out in various Geometry types (POLYGON, MULTIPOLYGON, LINESTRING).
    """
    id = models.CharField(max_length=36, primary_key=True)

    aanwijzingsdatum = models.DateField(null=True)
    architect = models.CharField(max_length=128, null=True)
    beperking = models.IntegerField(null=True)
    beschrijving = models.TextField(null=True)
    complex_id = models.CharField(max_length=36, null=True)
    afbeelding = models.CharField(max_length=36, null=True)
    functie = models.CharField(max_length=128, null=True)
    in_onderzoek = models.CharField(max_length=3, null=True)
    monumentnummer = models.IntegerField(null=True)
    naam = models.CharField(max_length=255, null=True)
    opdrachtgever = models.CharField(max_length=128, null=True)
    pand_sleutel = models.BigIntegerField(default=0)
    periode_start = models.IntegerField(null=True)
    periode_eind = models.IntegerField(null=True)
    coordinaten = models.PointField(null=True, srid=28992)
    geometrie = models.GeometryCollectionField(null=True, srid=28992)
    redengevende_omschrijving = models.TextField(null=True)
    status = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "Monument {}".format(self.id)


class Complex(models.Model):
    """
    Complex model
    NOOT: 'status' is geen attribuut in stelselpedia, is toegevoegd om aan te geven
    of het complex een [Rijksmomument, Gemeentelijk monument, Geen status] is.
    """
    id = models.CharField(max_length=36, primary_key=True)

    naam = models.CharField(max_length=255, null=True)
    monumentnummer = models.IntegerField(null=True)
    beschrijving = models.TextField(null=True)
    status = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "Complex {}".format(self.id)
