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
    betreft_pand = serializers.SerializerMethodField()
    heeft_situeringen = serializers.SerializerMethodField()
    heeft_als_grondslag_beperking = serializers.SerializerMethodField()

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

    def get_betreft_pand(self, obj):
        if (obj.betreft_pand):
            api_address = '{}://{}/bag/pand/{}/'.format(
                self.context['request'].scheme,
                self.context['request'].get_host(),
                str(obj.betreft_pand))
        else:
            api_address = None
        return {"href": api_address}

    def get_heeft_als_grondslag_beperking(self, obj):
        if (obj.heeft_als_grondslag_beperking):
            api_address = '{}://{}/wkpb/beperking/{}/'.format(
                self.context['request'].scheme,
                self.context['request'].get_host(),
                str(obj.heeft_als_grondslag_beperking))
        else:
            api_address = None
        return {"href": api_address}


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    monumentgeometrie = serializers.SerializerMethodField()
    complex_beschrijving = serializers.SerializerMethodField()

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


class SitueringSerializer(HALSerializer):
    _display = serializers.SerializerMethodField()
    betreft_nummeraanduiding = serializers.SerializerMethodField()
    hoort_bij_monument = serializers.SerializerMethodField()

    filter_fields = ('monument_id')

    class Meta:
        model = Situering
        fields = ['_display',
                  'id',
                  'situering_nummeraanduiding',
                  'betreft_nummeraanduiding',
                  'eerste_situering',
                  'hoort_bij_monument'
                  ]

    def get_betreft_nummeraanduiding(self, obj):
        if (obj.betreft_nummeraanduiding):
            api_address = '{}://{}/bag/nummeraanduiding/{}/'.format(
                self.context['request'].scheme,
                self.context['request'].get_host(),
                str(obj.betreft_nummeraanduiding))
        else:
            api_address = None
        return {"href": api_address}

    def get_hoort_bij_monument(self, obj):
        if (obj.hoort_bij_monument):
            api_address = '{}://{}/monumenten/monumenten/{}/'.format(
                self.context['request'].scheme,
                self.context['request'].get_host(),
                str(obj.hoort_bij_monument))
        else:
            api_address = None
        return {"href": api_address}

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
