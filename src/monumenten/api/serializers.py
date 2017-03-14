from rest_framework import serializers

from monumenten.api.rest import HALSerializer
from monumenten.dataset.models import Situering, Monument

OPENFIELDS = ['id',  # Identificerende sleutel monument
              'monumentnummer',  # Monumentnummer
              'naam',  # Monumentnaam
              'status',  # Monumentstatus
              'aanwijzingsdatum',  # Monument aanwijzingsdatum
              'pand_sleutel',  # Betreft [BAG:Pand] (Sleutelverzendend)
              # 'bag_pand',         # [BAG:Pand] ophalen uit BAG
              'complex_id',  # Identificerende sleutel complex
              'complex_naam',  # Complexnaam)
              'beperking',  # Heeft als grondslag [Wkpb:Beperking]
              'situering',  # De situering (adressen) van de panden
              'coordinaten',  # Monumentcoördinaten
              'geometrie',  # Geometrie van document
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


class MonumentSerializerNonAuth(HALSerializer):
    complex_id = serializers.SerializerMethodField()
    complex_naam = serializers.SerializerMethodField()
    situering = serializers.SerializerMethodField()

    class Meta:
        model = Monument
        fields = OPENFIELDS

    @staticmethod
    def get_complex_id(obj):
        if obj.complex:
            return str(obj.complex.external_id)

    @staticmethod
    def get_complex_naam(obj):
        if obj.complex:
            return str(obj.complex.complex_naam)

    def get_situering(self, obj):
        nr_of_situeringen = obj.situeringen.count()
        servername = self.context['request']._request.META['SERVER_NAME']
        serverport = self.context['request']._request.META['SERVER_PORT']
        api_address = 'https://{}:{}/monumenten/situeringen/?monumenten_id={}'
        return {"count": nr_of_situeringen,
                "href": api_address.format(servername,
                                           serverport,
                                           str(obj.monumentnummer))}


class MonumentSerializerAuth(MonumentSerializerNonAuth):
    class Meta:
        model = Monument
        fields = OPENFIELDS + NON_OPENFIELDS


class SitueringSerializer(HALSerializer):
    _display = serializers.SerializerMethodField()
    filter_fields = ('monument_id')

    class Meta:
        model = Situering
        fields = ['_display',
                  'situering_nummeraanduiding',
                  'eerste_situering'
                  ]

    @staticmethod
    def get__display(obj):
        """
        Gekopieerd vanuit BAG, straat voor toegevoegd

        :param obj:
        :return: displayfield met adres
        """
        toevoegingen = [obj.straat]

        toevoeging = obj.huisnummertoevoeging

        if obj.huisnummer:
            toevoegingen.append(str(obj.huisnummer))

        if obj.huisletter:
            toevoegingen.append(str(obj.huisletter))

        if toevoeging:
            tv = str(toevoeging)
            split_tv = " ".join([c for c in tv])
            toevoegingen.append(split_tv)

        return ' '.join(toevoegingen)
