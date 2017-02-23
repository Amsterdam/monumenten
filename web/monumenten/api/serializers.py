from rest_framework import serializers
from monumenten.dataset.models import Monument


class MonumentSerializer(serializers.ModelSerializer):
    situering = serializers.RelatedField(many=True)

    class Meta:
        model = Monument
        fields = ('monumentnummer', 'naam', 'type', 'status', 'architect',
                  'aanwijzingsdatum', 'opdrachtgever', 'periode_start',
                  'functie', 'pand_sleutel', 'coordinaten', 'geometrie', 'beperking',
                  'in_onderzoek', 'beschrijving', 'redengevende_omschrijving',
                  'afbeelding', 'complex_id', 'complex_naam')
