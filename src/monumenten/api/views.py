# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

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

    class Meta(object):
        model = Monument
        fields = ('betreft_pand',)


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
