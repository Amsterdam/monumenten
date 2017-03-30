from rest_framework import serializers

from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument, Complex
import json


OPENFIELDS_MONUMENT = ['id',
                       'monumentnummer',
                       'monumentnaam',
                       'monumentstatus',
                       'monument_aanwijzingsdatum',
                       'betreft_pand',
                       'display_naam',
                       'heeft_als_grondslag_beperking',
                       'heeft_situeringen',
                       'monumentcoordinaten',
                       'ligt_in_complex',
                       ]

NON_OPENFIELDS_MONUMENT = ['architect_ontwerp_monument',
                           'monumenttype',
                           'opdrachtgever_bouw_monument',
                           'bouwjaar_start_bouwperiode_monument',
                           'bouwjaar_eind_bouwperiode_monument',
                           'oorspronkelijke_functie_monument',
                           'monumentgeometrie',
                           'in_onderzoek',
                           'beschrijving_monument',
                           'redengevende_omschrijving_monument',
                           'complex_beschrijving',
                           'afbeelding',
                           ]

OPENFIELDS_COMPLEX = ['id',
                      'monumentnummer',
                      'complex_naam',
                      ]

NON_OPENFIELDS_COMPLEX = ['beschrijving']


class ComplexSerializerNonAuth(HALSerializer):

    class Meta:
        model = Complex
        fields = OPENFIELDS_COMPLEX


class ComplexSerializerAuth(ComplexSerializerNonAuth):

    class Meta:
        model = Complex
        fields = OPENFIELDS_COMPLEX + NON_OPENFIELDS_COMPLEX


class MonumentSerializerNonAuth(HALSerializer):

    ligt_in_complex = serializers.SerializerMethodField()
    heeft_situeringen = serializers.SerializerMethodField()

    class Meta:
        model = Monument
        fields = OPENFIELDS_MONUMENT

    def get_ligt_in_complex(self, obj):
        if not obj.complex:
            return None
        api_address = '{}://{}/monumenten/complexen/{}/'

        return {"href": api_address.format(self.context['request'].scheme,
                                           self.context['request'].get_host(),
                                           str(obj.complex.id))}

    def get_heeft_situeringen(self, obj):
        nr_of_situeringen = obj.situeringen.count()
        api_address = '{}://{}/monumenten/situeringen/?monument_id={}'
        return {"count": nr_of_situeringen,
                "href": api_address.format(self.context['request'].scheme,
                                           self.context['request'].get_host(),
                                           str(obj.id))}


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    monumentgeometrie = serializers.SerializerMethodField()
    complex_beschrijving = serializers.SerializerMethodField()
    afbeelding = serializers.SerializerMethodField()

    class Meta:
        model = Monument
        fields = OPENFIELDS_MONUMENT + NON_OPENFIELDS_MONUMENT

    @staticmethod
    def get_complex_beschrijving(obj):
        if obj.complex:
            return str(obj.complex.beschrijving)

    @staticmethod
    def get_monumentgeometrie(obj):
        if obj.monumentgeometrie:
            return json.loads(obj.monumentgeometrie.geojson)

    def get_afbeelding(self, obj):
        api_address = '{}://{}/monumenten/afbeeldingen/{}/'
        if obj.afbeelding is None:
            return {}
        return {"href": api_address.format(self.context['request'].scheme,
                                           self.context['request'].get_host(),
                                           str(obj.afbeelding))}


class SitueringSerializer(HALSerializer):
    _display = serializers.SerializerMethodField()
    filter_fields = ('monument_id')

    class Meta:
        model = Situering
        fields = ['_display',
                  'id',
                  'situering_nummeraanduiding',
                  'betreft_nummeraanduiding',
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
