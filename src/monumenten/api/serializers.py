from monumenten.dataset.models import Situering, Monument
from rest_framework import serializers

from monumenten.api.rest import DataSetSerializerMixin, HALSerializer

OPENFIELDS = ['id',  # Identificerende sleutel monument
              'monumentnummer',  # Monumentnummer
              'naam',  # Monumentnaam
              'status',  # Monumentstatus
              'aanwijzingsdatum',  # Monument aanwijzingsdatum
              'pand_sleutel',  # Betreft [BAG:Pand] (Sleutelverzendend)
              # 'bag_pand',         # [BAG:Pand] ophalen uit BAG
              # 'bag_nummeraanduiding', # [BAG:Nummeraanduiding] ophalen uit BAG
              'coordinaten',  # Monumentcoördinaten
              'complex_id',  # Identificerende sleutel complex
              'complex_naam',  # Complexnaam)
              'beperking',  # Heeft als grondslag [Wkpb:Beperking]
              'situering',  # De situering (adressen) van de panden
              ]

NON_OPENFIELDS = ['architect',
                  'type',
                  'opdrachtgever',
                  'periode_start',
                  'functie',
                  'geometrie',
                  'in_onderzoek',
                  'beschrijving',
                  'redengevende_omschrijving',
                  'afbeelding'
                  ]


# Ligt in [Complex]     Is al gedekt met complex_id en complex_naam
# Heeft [Situering]     Is al gedekt met situering
# Identificerende sleutel situering
# Situering nummeraanduiding
# Betreft [BAG:Nummeraanduiding]


class MonumentMixin(DataSetSerializerMixin):
    dataset = 'dataset'


class MonumentSerializerNonAuth(MonumentMixin, HALSerializer):
    complex_id = serializers.SerializerMethodField()
    complex_naam = serializers.SerializerMethodField()
    situering = serializers.SerializerMethodField()
    lookup_field = 'document_id'

    class Meta:
        model = Monument
        fields = OPENFIELDS

    @staticmethod
    def get_complex_id(obj):
        return str(obj.complex.external_id)

    @staticmethod
    def get_complex_naam(obj):
        return str(obj.complex.complex_naam)

    @staticmethod
    def get_situering(obj):
        nr_of_situeringen = obj.situeringen.count()
        api_address = '/monumenten/monument/{}/situering'
        return {"count": nr_of_situeringen,
                "href": api_address.format(str(obj.monumentnummer))}


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    class Meta:
        model = Monument
        fields = OPENFIELDS + NON_OPENFIELDS


class SitueringSerializer(MonumentMixin, HALSerializer):
    _display = serializers.SerializerMethodField

    class Meta:
        model = Situering
        fields = ('_display',
                  'situering_nummeraanduiding',
                  'eerste_situering'
                  )

    @staticmethod
    def get__display(obj):
        """
        Gekopieerd vanuit BAG, straat voor toegevoegd

        :param obj:
        :return: displayfield met adres
        """

        toevoegingen = [obj.straat]

        toevoeging = obj.huisnummer_toevoeging

        if obj.huisnummer:
            toevoegingen.append(str(obj.huisnummer))

        if obj.huisletter:
            toevoegingen.append(str(obj.huisletter))

        if toevoeging:
            tv = str(toevoeging)
            split_tv = " ".join([c for c in tv])
            toevoegingen.append(split_tv)

        return ' '.join(toevoegingen)
