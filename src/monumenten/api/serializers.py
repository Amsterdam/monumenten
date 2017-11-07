import json
import logging

from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry

from monumenten.api.rest import DisplayField
from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument, Complex

log = logging.getLogger(__name__)


OPENFIELDS_MONUMENT = [
    '_links',
    'identificerende_sleutel_monument',
    'monumentnummer',
    'monumentnaam',
    'monumentstatus',
    'monument_aanwijzingsdatum',
    'betreft_pand',
    '_display',
    'heeft_als_grondslag_beperking',
    'heeft_situeringen',
    'monumentcoordinaten',
    'ligt_in_complex',
    'in_onderzoek',
]

NON_OPENFIELDS_MONUMENT = [
    'architect_ontwerp_monument',
    'monumenttype',
    'opdrachtgever_bouw_monument',
    'bouwjaar_start_bouwperiode_monument',
    'bouwjaar_eind_bouwperiode_monument',
    'oorspronkelijke_functie_monument',
    'monumentgeometrie',
    'beschrijving_monument',
    'redengevende_omschrijving_monument',
    'beschrijving_complex',
]

OPENFIELDS_COMPLEX = [
    '_links',
    'identificerende_sleutel_complex',
    'monumentnummer_complex',
    'complexnaam',
    'monumenten',
    '_display',
]

NON_OPENFIELDS_COMPLEX = ['beschrijving_complex']


class BaseSerializer(object):

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

    def dict_with__links_self_href_id(self, path, id, id_name):
        return {
            "_links": {
                "self": {
                    "href": self.href_url(path.format(id))
                }
            },
            id_name: id
        }

    def dict_with_count_href(self, count, path):
        return {
            "count": count,
            "href": self.href_url(path)
        }


class ComplexSerializerNonAuth(BaseSerializer, HALSerializer):
    _links = serializers.SerializerMethodField()
    identificerende_sleutel_complex = serializers.SerializerMethodField()
    monumenten = serializers.SerializerMethodField()
    _display = DisplayField()

    class Meta(object):
        model = Complex
        fields = OPENFIELDS_COMPLEX

    def get__links(self, obj):
        return self.dict_with_self_href(
            '/monumenten/complexen/{}/'.format(obj.id))

    def get_identificerende_sleutel_complex(self, obj):
        return obj.id

    def get_monumenten(self, obj):
        nr_monumenten = obj.monumenten.count()
        path = '/monumenten/monumenten/?complex_id={}'.format(obj.id)
        return self.dict_with_count_href(nr_monumenten, path)


class ComplexSerializerAuth(ComplexSerializerNonAuth):

    class Meta(object):
        model = Complex
        fields = OPENFIELDS_COMPLEX + NON_OPENFIELDS_COMPLEX


class MonumentSerializerNonAuth(BaseSerializer, HALSerializer):

    _links = serializers.SerializerMethodField()
    _display = DisplayField()
    ligt_in_complex = serializers.SerializerMethodField()
    betreft_pand = serializers.SerializerMethodField()
    heeft_situeringen = serializers.SerializerMethodField()
    heeft_als_grondslag_beperking = serializers.SerializerMethodField()
    identificerende_sleutel_monument = serializers.SerializerMethodField()

    class Meta(object):
        model = Monument
        fields = OPENFIELDS_MONUMENT

    def get_identificerende_sleutel_monument(self, obj):
        return obj.id

    def get_ligt_in_complex(self, obj):
        if obj.complex:
            return self.dict_with__links_self_href_id(
                path='/monumenten/complexen/{}/',
                id=obj.complex.id,
                id_name='identificerende_sleutel_complex')

    def get_heeft_situeringen(self, obj):
        nr_of_situeringen = obj.situeringen.count()
        path = '/monumenten/situeringen/?monument_id={}'.format(
            str(obj.id))
        return self.dict_with_count_href(nr_of_situeringen, path)

    def get_betreft_pand(self, obj):
        if obj.betreft_pand:
            return self.dict_with__links_self_href_id(path='/bag/pand/{}/',
                                                      id=obj.betreft_pand,
                                                      id_name='pandidentificatie')

    def get_heeft_als_grondslag_beperking(self, obj):
        if obj.heeft_als_grondslag_beperking:
            return self.dict_with__links_self_href_id(
                path='/wkpb/beperking/{}/',
                id=obj.heeft_als_grondslag_beperking,
                id_name='id')

    def get__links(self, obj):
        return self.dict_with_self_href(
            '/monumenten/monumenten/{}/'.format(
                obj.id))


# Source: https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&SERVICE=wfs&typeName=unesco&Version=2.0.0&outputFormat=geojson
UNESCO_GEBIED = '{"type": "Polygon", "coordinates": [[[121876.541, 486607.417], [121912.241, 486624.117], [121959.041, 486645.317], [121989.841, 486661.517], [122068.441, 486718.517], [122099.741, 486737.317], [122142.841, 486617.017], [122164.441, 486623.417], [122187.141, 486610.917], [122230.441, 486602.417], [122297.941, 486594.517], [122370.741, 486553.517], [122377.441, 486531.217], [122420.541, 486544.017], [122541.241, 486476.917], [122536.341, 486459.917], [122539.441, 486440.017], [122558.741, 486372.117], [122558.841, 486349.417], [122538.941, 486251.017], [122540.941, 486238.017], [122157.041, 486119.717], [122161.541, 486104.617], [121997.341, 486054.017], [121974.041, 486131.917], [121549.341, 486004.917], [120951.041, 486142.317], [120580.841, 486557.817], [120515.641, 486521.117], [120489.641, 486579.117], [120452.741, 486654.617], [120560.841, 486711.917], [120500.141, 486828.017], [120552.041, 486856.317], [120402.241, 487217.817], [120523.041, 487266.917], [120473.041, 487388.017], [120585.041, 487433.017], [120518.841, 487612.917], [120647.041, 487656.217], [120610.041, 487759.017], [120739.941, 487802.717], [120708.241, 487890.217], [120810.241, 487924.317], [120773.641, 488083.417], [120876.041, 488112.117], [120836.141, 488284.517], [120893.541, 488300.317], [120909.341, 488332.817], [121024.741, 488458.917], [121126.341, 488377.317], [121323.641, 488192.917], [121363.641, 488170.817], [121459.341, 488079.217], [121433.141, 488043.017], [121460.241, 488015.517], [121434.341, 487980.917], [121431.441, 487869.417], [121441.341, 487844.117], [121451.441, 487838.517], [121416.041, 487808.617], [121372.341, 487769.017], [121297.841, 487684.117], [121258.241, 487633.317], [121204.141, 487567.517], [121162.941, 487508.417], [121120.041, 487377.617], [121106.741, 487276.917], [121075.941, 487052.917], [121051.741, 486932.517], [121051.303867, 486914.6988424], [121052.414915, 486903.564718], [121055.2312066, 486891.4440458], [121067.9343244, 486865.917], [121069.8509907, 486859.3233963], [121069.441, 486852.917], [121060.141, 486832.617], [121046.9074153, 486804.0879478], [121092.4967315, 486750.0571864], [121122.2693461, 486714.9584635], [121142.2595302, 486703.5779685], [121180.2196138, 486692.6229125], [121241.0408122, 486679.5406612], [121276.9806113, 486674.9671913], [121303.7759645, 486674.1163131], [121328.9763561, 486673.3717948], [121355.1337247, 486674.1163131], [121369.6212916, 486674.7943566], [121364.5621351, 486664.2555651], [121360.940144, 486656.8689374], [121359.2616369, 486652.1207336], [121357.1729969, 486639.9919216], [121348.3722272, 486582.0267985], [121536.6498369, 486539.160014], [121534.3257501, 486553.2298917], [121532.8371194, 486567.69482], [121533.7940963, 486581.4152298], [121536.4523655, 486600.7727074], [121543.2575345, 486599.0709511], [121553.6779496, 486597.9009937], [121568.8832492, 486597.5819144], [121663.2442094, 486597.3995833], [121746.2429677, 486592.0512065], [121781.0586987, 486589.4985721], [121795.8668854, 486588.7605656], [121802.4290127, 486588.8994844], [121808.4182559, 486589.5940788], [121821.8463127, 486591.4173891], [121838.3123914, 486594.0915775], [121850.4834666, 486597.791378], [121876.541, 486607.417]]]}' #noqa
unesco = GEOSGeometry(UNESCO_GEBIED, srid=28992)
unesco.transform(4326)


class MonumentSerializerMap(serializers.ModelSerializer):
    """
    Speciale Serializer voor POC koppeling maps.amsterdam.nl
    """
    COORDS = serializers.SerializerMethodField()
    FILTER = serializers.SerializerMethodField()
    LABEL = serializers.SerializerMethodField()
    LATMAX = serializers.SerializerMethodField()
    LNGMAX = serializers.SerializerMethodField()
    SELECTIE = serializers.SerializerMethodField()
    TYPE = serializers.SerializerMethodField()
    VOLGNR = serializers.SerializerMethodField()

    class Meta(object):
        model = Monument
        fields = ['COORDS', 'FILTER', 'LABEL', 'LATMAX', 'LNGMAX', 'SELECTIE', 'TYPE', 'VOLGNR']

    def get_COORDS(self, obj):
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            return f'{obj.monumentcoordinaten.x},{obj.monumentcoordinaten.y}||'
        return f'0,0||'

    def get_FILTER(self, obj):
        in_unesco = False
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            in_unesco = obj.monumentcoordinaten.intersects(unesco)
        return f"{obj.monumenttype}||{'Y' if in_unesco else 'N'}"

    def get_LABEL(self, obj):
        return obj.monumentstatus

    def get_LATMAX(self, obj):
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            return obj.monumentcoordinaten.x
        return "0"

    def get_LNGMAX(self, obj):
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            return obj.monumentcoordinaten.y
        return "0"

    def get_SELECTIE(self, obj):
        return "RIJKS" if obj.monumentstatus == 'Rijksmonument' else 'GEMEENTE'

    def get_TYPE(self, obj):
        return "punt"

    def get_VOLGNR(self, obj):
        return obj.monumentnummer


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    monumentgeometrie = serializers.SerializerMethodField()
    beschrijving_complex = serializers.SerializerMethodField()

    class Meta(object):
        model = Monument
        fields = OPENFIELDS_MONUMENT + NON_OPENFIELDS_MONUMENT

    @staticmethod
    def get_beschrijving_complex(obj):
        if obj.complex:
            return str(obj.complex.beschrijving_complex)

    @staticmethod
    def get_monumentgeometrie(obj):
        if obj.monumentgeometrie:
            return json.loads(obj.monumentgeometrie.geojson)


class SitueringSerializer(BaseSerializer, HALSerializer):

    _display = DisplayField()

    _links = serializers.SerializerMethodField()
    betreft_nummeraanduiding = serializers.SerializerMethodField()
    hoort_bij_monument = serializers.SerializerMethodField()
    identificerende_sleutel_situering = serializers.SerializerMethodField()

    filter_fields = ('monument_id')

    class Meta(object):
        model = Situering
        fields = [
            '_links',
            '_display',
            'identificerende_sleutel_situering',
            'situering_nummeraanduiding',
            'betreft_nummeraanduiding',
            'eerste_situering',
            'hoort_bij_monument',
       ]

    def get_identificerende_sleutel_situering(self, obj):
        return obj.id

    def get_betreft_nummeraanduiding(self, obj):
        if obj.betreft_nummeraanduiding:
            return self.dict_with__links_self_href_id(
                path='/bag/nummeraanduiding/{}/',
                id=obj.betreft_nummeraanduiding,
                id_name='nummeraanduidingidentificatie')

    def get_hoort_bij_monument(self, obj):
        if obj.hoort_bij_monument:
            return self.dict_with__links_self_href_id(
                path='/monumenten/monumenten/{}/',
                id=obj.hoort_bij_monument,
                id_name='identificerende_sleutel_monument')

    def get__links(self, obj):
        return self.dict_with_self_href(
            '/monumenten/situeringen/{}/'.format(obj.id))
