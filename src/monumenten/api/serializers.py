import json
import logging

from rest_framework import serializers

from monumenten.api.rest import DisplayField
from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument, Complex
from monumenten.dataset.static_data import UNESCO_GEBIED

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
            return f'{obj.monumentcoordinaten.x:.7f},{obj.monumentcoordinaten.y:.7f}||'
        return f'0,0||'

    def get_FILTER(self, obj):
        in_unesco = False
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            in_unesco = obj.monumentcoordinaten.intersects(UNESCO_GEBIED)
        return f"{obj.monumenttype}||{'Y' if in_unesco else 'N'}"

    def get_LABEL(self, obj):
        return obj.monumentstatus

    def get_LATMAX(self, obj):
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            return f"{obj.monumentcoordinaten.y:.7f}"
        return "0"

    def get_LNGMAX(self, obj):
        if obj.monumentcoordinaten is not None:
            obj.monumentcoordinaten.transform(4326)
            return f"{obj.monumentcoordinaten.x:.7f}"
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
