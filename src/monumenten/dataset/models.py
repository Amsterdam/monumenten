from django.contrib.gis.db import models


class Complex(models.Model):
    """
    Complex model
    -- aanvulling op stelselpedia --
    status: geeft [Rijksmomument, Gemeentelijk monument, Geen status] aan.
    external_id: id conform AMISExport.xml
    """
    external_id = models.CharField(max_length=36, null=True, db_index=True)

    beschrijving = models.TextField(null=True)
    monumentnummer = models.IntegerField(null=True)
    complex_naam = models.CharField(max_length=255, null=True)
    complexstatus = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "Complex {}".format(self.id)


class Monument(models.Model):
    """
    Monument model
    NOTE: 'geometrie' type is GeometryCollectionField, possibly in future
    (e.g. for searching) this needs to be split out in various Geometry types
    (POLYGON, MULTIPOLYGON, LINESTRING).
    -- aanvulling op stelselpedia --
    external_id: id conform AMISExport.xml
    """
    external_id = models.CharField(max_length=36, null=True)

    monument_aanwijzingsdatum = models.DateField(null=True)
    architect_ontwerp_monument = models.CharField(max_length=128, null=True)
    beperking = models.IntegerField(null=True)
    beschrijving_monument = models.TextField(null=True)
    monumentcoordinaten = models.PointField(null=True, srid=28992)
    afbeelding = models.CharField(max_length=36, null=True)
    oorspronkelijke_functie_monument = models.CharField(max_length=128, null=True)
    monumentgeometrie = models.GeometryCollectionField(null=True, srid=28992)
    in_onderzoek = models.CharField(max_length=3, null=True)
    monumentnummer = models.IntegerField(null=True)
    monumentnaam = models.CharField(max_length=255, null=True)
    display_naam = models.CharField(max_length=255, null=True)
    opdrachtgever_bouw_monument = models.CharField(max_length=128, null=True)
    betreft = models.CharField(max_length=16, null=True)
    bouwjaar_start_bouwperiode_monument = models.IntegerField(null=True)
    bouwjaar_eind_bouwperiode_monument = models.IntegerField(null=True)
    redengevende_omschrijving_monument = models.TextField(null=True)
    monumentstatus = models.CharField(max_length=128, null=True)
    monumenttype = models.CharField(max_length=128, null=True)
    heeft_als_grondslag = models.CharField(max_length=36, null=True)

    complex = models.ForeignKey(Complex, related_name='monumenten', null=True)

    def __str__(self):
        return "Monument {}".format(self.id)


class Situering(models.Model):
    """
    Situering model
    -- aanvulling op stelselpedia --
    eerste_situering: geeft aan welke situering de eerste is.
    adresgegevens.
    external_id: id conform AMISExport.xml
    """
    external_id = models.CharField(max_length=36, null=True)

    betreft = models.CharField(max_length=16, null=True)
    situering_nummeraanduiding = models.CharField(max_length=128, null=True)
    eerste_situering = models.CharField(max_length=3, null=True)

    huisnummer = models.IntegerField(null=True)
    huisletter = models.CharField(max_length=1, null=True)
    huisnummertoevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    straat = models.CharField(max_length=80, null=True)

    monument = models.ForeignKey(Monument, related_name='situeringen')

    def __str__(self):
        return "Situering {}".format(self.id)
