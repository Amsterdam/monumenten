from rest_framework import serializers

from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument
import json
from monumenten import settings


OPENFIELDS = ['id',  # Identificerende sleutel monument
              'monumentnummer',  # Monumentnummer
              'monumentnaam',  # Monumentnaam
              'monumentstatus',  # Monumentstatus
              'monument_aanwijzingsdatum',  # Monument aanwijzingsdatum
              'betreft_pand',  # Betreft [BAG:Pand] (Sleutelverzendend)
              'display_naam',  # Monumentnaam voor display
              'complex_id',  # Identificerende sleutel complex
              'complex_naam',  # Complexnaam)
              'heeft_als_grondslag_beperking',  # Heeft als grondslag [Wkpb:Beperking]
              'situering',  # De situering (adressen) van de panden
              'monumentcoordinaten',  # Monumentcoördinaten
              'monumentgeometrie',  # Geometrie van document
              ]

NON_OPENFIELDS = ['architect_ontwerp_monument',
                  'monumenttype',
                  'opdrachtgever_bouw_monument',
                  'bouwjaar_start_bouwperiode_monument',
                  'bouwjaar_eind_bouwperiode_monument',
                  'oorspronkelijke_functie_monument',
                  'geometrie',
                  'in_onderzoek',
                  'beschrijving_monument',
                  'redengevende_omschrijving_monument',
                  'afbeelding'
                  ]


class MonumentSerializerNonAuth(HALSerializer):
    complex_id = serializers.SerializerMethodField()
    complex_naam = serializers.SerializerMethodField()
    situering = serializers.SerializerMethodField()
    monumentgeometrie = serializers.SerializerMethodField()

    class Meta:
        model = Monument
        fields = OPENFIELDS

    @staticmethod
    def get_complex_id(obj):
        if obj.complex:
            return str(obj.complex.external_id)

    @staticmethod
    def get_complex_naam(obj):
        if obj.complex:
            return str(obj.complex.complex_naam)

    @staticmethod
    def get_monumentgeometrie(obj):
        if obj.monumentgeometrie:
            return json.loads(obj.monumentgeometrie.geojson)

    def get_situering(self, obj):
        nr_of_situeringen = obj.situeringen.count()
        api_address = '{}monumenten/situeringen/?monument_id={}'
        return {"count": nr_of_situeringen,
                "href": api_address.format(settings.DATAPUNT_API_URL,
                                           str(obj.id))}


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    class Meta:
        model = Monument
        fields = OPENFIELDS + NON_OPENFIELDS


class SitueringSerializer(HALSerializer):
    _display = serializers.SerializerMethodField()
    filter_fields = ('monument_id')

    class Meta:
        model = Situering
        fields = ['_display',
                  'situering_nummeraanduiding',
                  'eerste_situering'
                  ]

    @staticmethod
    def get__display(obj):
        """
        Gekopieerd vanuit BAG, straat voor toegevoegd

        :param obj:
        :return: displayfield met adres
        """
        toevoegingen = [obj.straat]

        toevoeging = obj.huisnummertoevoeging

        if obj.huisnummer:
            toevoegingen.append(str(obj.huisnummer))

        if obj.huisletter:
            toevoegingen.append(str(obj.huisletter))

        if toevoeging:
            tv = str(toevoeging)
            split_tv = " ".join([c for c in tv])
            toevoegingen.append(split_tv)

        return ' '.join(toevoegingen)
