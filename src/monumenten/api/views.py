# Create your views here.
import logging

import authorization_levels
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import serializers as rest_serializers
from rest_framework import response

from monumenten.api import serializers
from monumenten.dataset.models import Monument, Situering, Complex
from monumenten.dataset.static_data import UNESCO_GEBIED
from .rest import DatapuntViewSet

log = logging.getLogger(__name__)


class ComplexFilter(FilterSet):
    id = filters.CharFilter()

    class Meta(object):
        model = Complex
        fields = ('monumentnummer_complex',)


class ComplexViewSet(DatapuntViewSet):
    serializer_detail_class = serializers.ComplexSerializerNonAuth
    queryset = Complex.objects.all()
    filter_class = ComplexFilter

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.SCOPE_MON_RBC):
            return serializers.ComplexSerializerAuth
        return serializers.ComplexSerializerNonAuth


# max bbox sizes from mapserver
# RD  EXTENT      100000    450000   150000 500000
# WGS             52.03560, 4.58565  52.48769, 5.31360


def valid_rd(x, y):

    rd_x_min = 100000
    rd_y_min = 450000
    rd_x_max = 150000
    rd_y_max = 500000

    if not rd_x_min <= x <= rd_x_max:
        return False

    if not rd_y_min <= y <= rd_y_max:
        return False

    return True


def valid_lat_lon(lat, lon):

    lat_min = 52.03560
    lat_max = 52.48769
    lon_min = 4.58565
    lon_max = 5.31360

    if not lat_min <= lat <= lat_max:
        return False

    if not lon_min <= lon <= lon_max:
        return False

    return True


def convert_intput_to_float(value):

    x = None
    y = None
    radius = None
    err = None

    try:
        x, y, radius = value.split(',')
    except ValueError:
        return None, None, f"Not enough values x, y, radius {value}"

    # Converting to float
    try:
        x = float(x)
        y = float(y)
        radius = int(radius)
    except ValueError:
        return None, None, f"Invalid value {x} {y} {radius}"

    return x, y, radius, err


def validate_x_y(value):
    """
    Check if we get valid values
    """
    x = None
    y = None
    err = None
    point = radius = None

    x, y, radius, err = convert_intput_to_float(value)

    if err:
        return None, None, err

    # checking sane radius size
    if radius > 1000:
        return None, None, "radius too big"

    # Checking if the given coords are valid

    if valid_rd(x, y):
        point = Point(x, y, srid=28992)
    elif valid_lat_lon(x, y):
        point = Point(y, x, srid=4326).transform(28992, clone=True)
    else:
        err = "Coordinates recieved not within Amsterdam"

    return point, radius, err


class MonumentFilter(FilterSet):
    id = filters.CharFilter()

    locatie = filters.CharFilter(method="locatie_filter")
    betreft_pand = filters.CharFilter(field_name='betreft_pand__pand_id')

    class Meta(object):
        model = Monument
        fields = (
            'betreft_pand',
            'locatie',
            'complex_id',
        )

    def nummeraanduiding_filter(self, queryset, filer_name, value):
        """
        Locate monuments near nummeraanduiding

        TODO
        """

        # Ask bag-api for geolocation

        # Use location for location filter!
        pass

    def locatie_filter(self, queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 3 numerical values: x, y and radius
        The value given is broken up by ',' and coverterd
        to the value tuple
        """

        point, radius, err = validate_x_y(value)

        if err:
            log.exception(err)
            raise rest_serializers.ValidationError(err)
            # return queryset.none()

        # Creating one big queryset
        monumenten_g = queryset.filter(
            monumentgeometrie__dwithin=(point, D(m=radius))
        ).annotate(afstand=Distance('monumentgeometrie', point))

        monumenten_p = queryset.filter(
            monumentcoordinaten__dwithin=(point, D(m=radius))
        ).annotate(afstand=Distance('monumentcoordinaten', point))

        results = monumenten_g | monumenten_p

        return results.order_by('afstand')


class MonumentViewSet(DatapuntViewSet):
    serializer_detail_class = serializers.MonumentSerializerNonAuth
    queryset = Monument.objects.select_related('complex')
    filter_class = MonumentFilter

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.SCOPE_MON_RDM):
            return serializers.MonumentSerializerAuth
        return serializers.MonumentSerializerNonAuth


class MapsMonumentFilter(FilterSet):
    """
    Speciaal Filter voor POC koppeling maps.amsterdam.nl
    """
    SELECT = filters.CharFilter(method="select_filter")

    class Meta(object):
        model = Monument
        fields = ('SELECT',)

    def select_filter(self, queryset, _filter_name, value):
        """
        Filter based on the SELECT
        """
        status = 'Rijksmonument' if 'RIJKS' in value else 'Gemeentelijk monument'
        omschrijving_is_null = '_PLUS' not in value
        return queryset.filter(monumentstatus=status,
                               redengevende_omschrijving_monument__isnull=omschrijving_is_null)


class SimpleMonumentViewSet(MonumentViewSet):
    """
    Speciale ViewSet voor POC koppeling maps.amsterdam.nl
    """
    pagination_class = None
    serializer_detail_class = serializers.MonumentSerializerMap
    queryset = Monument.objects.filter(monumentnummer__isnull=False, monumentcoordinaten__isnull=False)
    filter_class = MapsMonumentFilter

    def get_serializer_class(self):
        return serializers.MonumentSerializerMap


class SimpleUnescoViewSet(DatapuntViewSet):
    """
    Speciale ViewSet voor POC koppeling maps.amsterdam.nl
    """
    pagination_class = None
    queryset = Monument.objects.all()

    def list(self, request, *args, **kwargs):
        polygon = UNESCO_GEBIED.coords[0]
        coords = list(map((lambda coords: f"{coords[0]:.7f},{coords[1]:.7f}"), polygon))
        coord_str = '|'.join(coords)
        return response.Response([{
            "VOLGNR": 9,
            "LABEL": "Grachtengordel Amsterdam Werelderfgoed (kerngebied)",
            "SELECTIE": "KERN",
            "TYPE": "vlak",
            "COORDS": f"{coord_str}||",
            "LATMAX": 52.3719254,
            "LNGMAX": 4.895345
        }])


class SitueringFilter(FilterSet):
    monument_id = filters.CharFilter()
    betreft_nummeraanduiding = filters.CharFilter()
    id = filters.CharFilter()

    class Meta(object):
        model = Situering
        fields = ('monument_id', 'betreft_nummeraanduiding')


class SitueringList(DatapuntViewSet):
    """
    De situering van een monument. Dit is ten opzichte van andere objecten in
    de openbare ruimte
    """
    queryset = Situering.objects.all()
    serializer_detail_class = serializers.SitueringSerializer
    serializer_class = serializers.SitueringSerializer
    filter_class = SitueringFilter
    queryset_detail = (Situering.objects.all())
