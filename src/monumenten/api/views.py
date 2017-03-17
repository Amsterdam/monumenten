# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from monumenten.api import serializers
from monumenten.dataset.models import Monument, Situering
from .rest import MonumentVS


class MonumentFilter(FilterSet):
    monument_id = filters.NumberFilter()

    class Meta:
        model = Monument
        fields = ('betreft_pand',)


class MonumentViewSet(MonumentVS):
    serializer_detail_class = serializers.MonumentSerializerNonAuth
    queryset = Monument.objects.select_related('complex')
    filter_class = MonumentFilter

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth


class SitueringFilter(FilterSet):
    monument_id = filters.NumberFilter()

    class Meta:
        model = Situering
        fields = ('monument_id',)


class SitueringList(MonumentVS):
    """
    De situering van een monument. Dit is ten opzichte van andere objecten in
    de openbare ruimte
    """
    queryset = Situering.objects.all()
    serializer_detail_class = serializers.SitueringSerializer
    serializer_class = serializers.SitueringSerializer
    filter_class = SitueringFilter
    queryset_detail = (Situering.objects.all())
