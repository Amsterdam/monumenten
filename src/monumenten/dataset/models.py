from django.contrib.gis.db import models


class Complex(models.Model):
    """
    Complex model
    -- aanvulling op stelselpedia --
    status: geeft [Rijksmomument, Gemeentelijk monument, Geen status] aan.
    external_id: id conform AMISExport.xml
    """
    id = models.CharField(max_length=36, primary_key=True)
    external_id = models.CharField(max_length=36, null=True, db_index=True)

    beschrijving_complex = models.TextField(null=True)
    monumentnummer_complex = models.IntegerField(null=True)
    complexnaam = models.CharField(max_length=255, null=True)
    complexstatus = models.CharField(max_length=128, null=True)

    def __str__(self):
        if self.complexnaam:
            return self.complexnaam
        if self.monumentnummer_complex:
            return self.monumentnummer_complex
        # Above as per be-1261 - fallback below (self.id is never null):
        return 'Complex {}'.format(self.id)


class Monument(models.Model):
    """
    Monument model
    NOTE: 'geometrie' type is GeometryCollectionField, possibly in future
    (e.g. for searching) this needs to be split out in various Geometry types
    (POLYGON, MULTIPOLYGON, LINESTRING).
    -- aanvulling op stelselpedia --
    external_id: id conform AMISExport.xml
    """
    id = models.CharField(max_length=36, primary_key=True)
    external_id = models.CharField(max_length=36, null=True)

    monument_aanwijzingsdatum = models.DateField(null=True)
    architect_ontwerp_monument = models.CharField(max_length=128, null=True)
    beschrijving_monument = models.TextField(null=True)
    monumentcoordinaten = models.PointField(null=True, srid=28992)
    afbeelding = models.CharField(max_length=36, null=True)
    oorspronkelijke_functie_monument = models.CharField(
        max_length=128, null=True)
    monumentgeometrie = models.GeometryCollectionField(null=True, srid=28992)
    in_onderzoek = models.CharField(max_length=3, null=True)
    monumentnummer = models.IntegerField(null=True)
    monumentnaam = models.CharField(max_length=255, null=True)
    display_naam = models.CharField(max_length=255, null=True)
    opdrachtgever_bouw_monument = models.CharField(max_length=128, null=True)
    betreft_pand = models.CharField(max_length=16, null=True)
    bouwjaar_start_bouwperiode_monument = models.IntegerField(null=True)
    bouwjaar_eind_bouwperiode_monument = models.IntegerField(null=True)
    redengevende_omschrijving_monument = models.TextField(null=True)
    monumentstatus = models.CharField(max_length=128, null=True)
    monumenttype = models.CharField(max_length=128, null=True)
    heeft_als_grondslag_beperking = models.CharField(max_length=15, null=True)

    complex = models.ForeignKey(Complex, related_name='monumenten', null=True)

    def __str__(self):
        if self.display_naam:
            return self.display_naam
        if self.monumentnummer:
            return str(self.monumentnummer)
        if self.situeringen:
            return repr(self.situeringen.first())
        return "Monument {}".format(self.id)


class Situering(models.Model):
    """
    Situering model
    -- aanvulling op stelselpedia --
    eerste_situering: geeft aan welke situering de eerste is.
    adresgegevens.
    external_id: id conform AMISExport.xml
    id: is automatisch en gebaseerd op een sequence. Deze id kan niet gebaseerd
    worden op de external_id, want die is niet uniek. Ook de combinatie
    monumenten-external-id en adress-external-id is niet uniek
    in de aangeleverde data.
    """
    id = models.AutoField(primary_key=True)
    external_id = models.CharField(max_length=36, null=True)

    betreft_nummeraanduiding = models.CharField(max_length=16, null=True)
    situering_nummeraanduiding = models.CharField(max_length=128, null=True)
    eerste_situering = models.CharField(max_length=3, null=True)

    huisnummer = models.IntegerField(null=True)
    huisletter = models.CharField(max_length=1, null=True)
    huisnummertoevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    straat = models.CharField(max_length=80, null=True)

    monument = models.ForeignKey(Monument, related_name='situeringen')

    @property
    def hoort_bij_monument(self):
        return self.monument_id

    def __str__(self):
        """
        Gekopieerd vanuit BAG, straat voor toegevoegd

        :return: displayfield met adres
        """
        toevoegingen = [self.straat]

        toevoeging = self.huisnummertoevoeging

        if self.huisnummer:
            toevoegingen.append(str(self.huisnummer))

        if self.huisletter:
            toevoegingen.append(str(self.huisletter))

        if toevoeging:
            tv = str(toevoeging)
            split_tv = " ".join([c for c in tv])
            toevoegingen.append(split_tv)

        return ' '.join(toevoegingen)
