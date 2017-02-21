from django.contrib.gis.db import models


class Monument(models.Model):
    """
    Monument model
    """
    id = models.CharField(max_length=36, primary_key=True)

    aanwijzingsdatum = models.DateField(null=True)
    architect = models.CharField(max_length=128, null=True)
    beperking = models.IntegerField(null=True)
    beschrijving = models.TextField(null=True)
    complex_id = models.CharField(max_length=36, null=True)
    complex_naam = models.CharField(max_length=255, null=True)
    complex_nummer = models.IntegerField(null=True)
    afbeelding = models.CharField(max_length=36, null=True)
    functie = models.CharField(max_length=128, null=True)
    in_onderzoek = models.CharField(max_length=3, null=True)
    monumentnummer = models.IntegerField(null=True)
    naam = models.CharField(max_length=255, null=True)
    opdrachtgever = models.CharField(max_length=128, null=True)
    pand_sleutel = models.BigIntegerField(default=0)
    periode_start = models.IntegerField(null=True)
    periode_eind = models.IntegerField(null=True)
    punt = models.PointField(null=True, srid=28992)
    polygoon = models.PolygonField(null=True, srid=28992)
    redengevende_omschrijving = models.TextField(null=True)
    status = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "Monument {}".format(self.id)
