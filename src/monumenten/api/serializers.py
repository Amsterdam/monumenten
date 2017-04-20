from rest_framework import serializers

from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument, Complex
import json


OPENFIELDS_MONUMENT = ['_links',
                       'id',
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

OPENFIELDS_COMPLEX = ['_links',
                      'id',
                      'monumentnummer',
                      'complex_naam',
                      ]

NON_OPENFIELDS_COMPLEX = ['beschrijving']


class Base(object):

    def href_url(self, path):
        """Prepend scheme and hostname"""
        base_url = '{}://{}'.format(
            self.context['request'].scheme,
            self.context['request'].get_host())
        return base_url + path

    def dict_with_self_href(self, path):
        return {
            "self": {
                "href": self.href_url(path)
            }
        }

    def dict_with__links_self_href_id(self, path, id):
        return {
            "_links": {
                "self": {
                    "href": self.href_url(path.format(id))
                }
            },
            "id": id
        }

    def dict_with_count_href(self, count, path):
        return {
            "count": count,
            "href": self.href_url(path)
        }


class ComplexSerializerNonAuth(Base, HALSerializer):
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Complex
        fields = OPENFIELDS_COMPLEX

    def get__links(self, obj):
        return self.dict_with_self_href('/monumenten/complexen/{}/'.format(obj.id))


class ComplexSerializerAuth(ComplexSerializerNonAuth):

    class Meta:
        model = Complex
        fields = OPENFIELDS_COMPLEX + NON_OPENFIELDS_COMPLEX


class MonumentSerializerNonAuth(Base, HALSerializer):

    _links = serializers.SerializerMethodField()
    ligt_in_complex = serializers.SerializerMethodField()
    betreft_pand = serializers.SerializerMethodField()
    heeft_situeringen = serializers.SerializerMethodField()
    heeft_als_grondslag_beperking = serializers.SerializerMethodField()

    class Meta:
        model = Monument
        fields = OPENFIELDS_MONUMENT

    def get_ligt_in_complex(self, obj):
        if obj.complex:
            return self.dict_with__links_self_href_id('/monumenten/complexen/{}/', obj.complex.id)

    def get_heeft_situeringen(self, obj):
        nr_of_situeringen = obj.situeringen.count()
        path = '/monumenten/situeringen/?monument_id={}'.format(str(obj.id))
        return self.dict_with_count_href(nr_of_situeringen, path)

    def get_betreft_pand(self, obj):
        if obj.betreft_pand:
            return self.dict_with__links_self_href_id('/bag/pand/{}/', obj.betreft_pand)

    def get_heeft_als_grondslag_beperking(self, obj):
        if obj.heeft_als_grondslag_beperking:
            return self.dict_with__links_self_href_id('/wkpb/beperking/{}/', obj.heeft_als_grondslag_beperking)

    def get__links(self, obj):
        return self.dict_with_self_href('/monumenten/monumenten/{}/'.format(obj.id))


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


class SitueringSerializer(Base, HALSerializer):
    _display = serializers.SerializerMethodField()
    _links = serializers.SerializerMethodField()
    betreft_nummeraanduiding = serializers.SerializerMethodField()
    hoort_bij_monument = serializers.SerializerMethodField()

    filter_fields = ('monument_id')

    class Meta:
        model = Situering
        fields = ['_links',
                  '_display',
                  'id',
                  'situering_nummeraanduiding',
                  'betreft_nummeraanduiding',
                  'eerste_situering',
                  'hoort_bij_monument',
                  ]

    def get_betreft_nummeraanduiding(self, obj):
        if obj.betreft_nummeraanduiding:
            return self.dict_with__links_self_href_id('/bag/nummeraanduiding/{}/', obj.betreft_nummeraanduiding)

    def get_hoort_bij_monument(self, obj):
        if obj.hoort_bij_monument:
            return self.dict_with__links_self_href_id('/monumenten/monumenten/{}/', obj.hoort_bij_monument)

    def get__links(self, obj):
        return self.dict_with_self_href('/monumenten/situeringen/{}/'.format(obj.id))

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
