# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from rest_framework import serializers as rest_serializers

from monumenten.api import serializers
from monumenten.dataset.models import Monument, Situering, Complex
from .rest import DatapuntViewSet

import logging

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
        if self.request.is_authorized_for('MON/RC') or \
                self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
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

    # verblijfs object filter

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
        if self.request.is_authorized_for('MON/RC') or \
                self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        return serializers.MonumentSerializerNonAuth


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
