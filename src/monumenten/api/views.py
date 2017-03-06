# from django.shortcuts import render

# Create your views here.

from authorization_django import levels as authorization_levels
from monumenten.dataset.models import Monument, Situering
from rest_framework import mixins, generics

from monumenten.api import serializers


class MonumentList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Monument.objects.select_related('complex')

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MonumentDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.LEVEL_EMPLOYEE):
            return serializers.MonumentSerializerAuth
        else:
            return serializers.MonumentSerializerNonAuth

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self, *args):
        """
        Get using pk
        """
        pk = self.args[0]
        return Monument.objects.get(pk=pk)


class SitueringDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = serializers.SitueringSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self, *args):
        """
        Get using pk
        """
        pk = self.args[0]
        return Situering.objects.get(pk=pk)


class SitueringList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Situering.objects.all()
    serializer_class = serializers.SitueringSerializer

    def get_queryset(self):

        if len(self.args):
            return Situering.objects.filter(monument_id=self.args[0]).order_by('eerste_situering')
        else:
            return Situering.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
