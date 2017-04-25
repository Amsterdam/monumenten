# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from monumenten.api import serializers
from monumenten.dataset.models import Monument, Situering, Complex
from .rest import DatapuntViewSet


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
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.ComplexSerializerAuth
        return serializers.ComplexSerializerNonAuth


class MonumentFilter(FilterSet):
    id = filters.CharFilter()

    locatie = filters.CharFilter(method="locatie_filter")

    # verblijfs object filter

    class Meta(object):
        model = Monument
        fields = (
            'betreft_pand',
            'locatie',
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
        try:
            x, y, radius = value.split(',')
        except ValueError:
            return queryset.none()

        # Converting , to . and then to float
        x = float(x)
        y = float(y)
        radius = int(radius)

        # Checking if the given coords are in RD, otherwise converting

        if y > 10:
            point = Point(x, y, srid=28992)
        else:
            point = Point(y, x, srid=4326).transform(28992, clone=True)

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
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        return serializers.MonumentSerializerNonAuth


class SitueringFilter(FilterSet):
    monument_id = filters.CharFilter()
    id = filters.CharFilter()

    class Meta(object):
        model = Situering
        fields = ('monument_id',)


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
