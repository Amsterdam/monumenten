# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from monumenten.dataset.models import Monument, Situering
from rest_framework import mixins, generics

from monumenten.api import serializers


class MonumentList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Monument.objects.select_related('complex')

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE) or True:
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MonumentDetail(mixins.ListModelMixin, generics.GenericAPIView):
    pass


class SitueringDetail(mixins.ListModelMixin, generics.GenericAPIView):
    pass


class SitueringList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Situering.objects.all()
    serializer_class = serializers.SitueringSerializer

    def get_queryset(self):
        monumentnummer = self.request.query_params.get('monumentnummer', None)
        if monumentnummer:
            return Situering.objects.filter(monumentnummer=monumentnummer)
        else:
            return Situering.objects.all()
