# from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from monumenten.dataset.models import Monument


#TODO selectie van de rest api?
class MonumentList(generics.ListAPIView):
    queryset = Monument.objects.all().prefetch_related('')
