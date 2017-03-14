# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from django.http import Http404
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import mixins, generics, metadata

from monumenten.api import serializers
from monumenten.dataset.models import Monument, Situering
from .rest import MonumentVS


class ExpansionMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            full=dict(
                type="string",
                description="If present, related entities are inlined",
                required=False
            )
        )
        return result


class BaseMixin(generics.GenericAPIView):
    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth


class AuthMixin():
    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth


class MonumentViewSet(AuthMixin, MonumentVS):
    serializer_detail_class = serializers.MonumentSerializerNonAuth
    metadata_class = ExpansionMetadata
    queryset = Monument.objects.select_related('complex')


class MonumentFilter(FilterSet):
    monument_id = filters.CharFilter()

    class Meta:
        model = Monument
        fields = ('pand_sleutel',)


class MonumentDetail(AuthMixin, MonumentVS):
    serializer_detail_class = serializers.MonumentSerializerNonAuth
    metadata_class = ExpansionMetadata
    queryset = Monument.objects.select_related('complex')
    filter_class = MonumentFilter

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        """
        Get using pk
        """
        result = Http404('<h1>Monument kan niet worden gevonden</h1>')
        if 'pk' in self.kwargs:
            try:
                pk = int(self.kwargs['pk'])
            except ValueError:
                result = self.get_by_parameter(*args, **kwargs)
            else:
                result = Monument.objects.get(pk=pk)
        return result


class SitueringDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
    Situering van een monument

    De Situering geeft de positie van het monument ten opzichte van andere
    objecten in de openbare ruimte weer
    """
    serializer_class = serializers.SitueringSerializer
    queryset = Situering.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self, *args):
        """
        Get using pk
        """
        pk = self.args[0]
        result = Situering.objects.get(pk=pk)
        if not result:
            result = Http404('<h1>Situering bestaat niet</h1>')
        return result


class SitueringList(MonumentVS):
    """
    De situering van een monument. Dit is ten opzichte van andere objecten in
    de openbare ruimte
    """
    metadata_class = ExpansionMetadata
    serializer_detail_class = serializers.SitueringSerializer
    serializer_class = serializers.SitueringSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        """
        Get using pk
        """
        result = Http404('<h1>Monument kan niet worden gevonden</h1>')
        if 'pk' in self.kwargs:
            try:
                pk = int(self.kwargs['pk'])
            except ValueError:
                pass
            else:
                result = Monument.objects.get(pk=pk)
        return result
