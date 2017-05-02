import logging

from django.db import connection
from monumenten.dataset.models import Monument, Situering

log = logging.getLogger(__name__)


def search_landelijk_id_nummeraanduiding(sleutelverzendend):
    with connection.cursor() as cursor:
        cursor.execute("select landelijk_id FROM bag_nummeraanduiding where id='{}'".format(sleutelverzendend))
        row = cursor.fetchone()
    return row


def search_landelijk_id_pand(sleutelverzendend):
    with connection.cursor() as cursor:
        cursor.execute("select landelijk_id FROM bag_pand where id='{}'".format(sleutelverzendend))
        row = cursor.fetchone()
    return row


def convert_monumenten():
    for monument in Monument.objects.all():
        print('monument id', monument.id)
        print('betreft_pand', monument.betreft_pand)
        if not monument.betreft_pand:
            print('skip update betreft_pand, is empty')
        elif monument.betreft_pand.__len__() == 14:
            landelijk_id = search_landelijk_id_pand(monument.betreft_pand)
            if landelijk_id:
                print('updating betreft_pand naar landelijk_id', landelijk_id[0])
                monument.betreft_pand = landelijk_id[0]
                monument.save()
            else:
                print('landelijk_id_not_found!')
        else:
            print('skip update betreft_pand, already has landelijk_id')


def convert_situeringen():
    for situering in Situering.objects.all():
        print('situering id', situering.id)
        print('betreft_nummeraanduiding', situering.betreft_nummeraanduiding)
        if not situering.betreft_nummeraanduiding:
            print('skip update betreft_nummeraanduiding, is empty')
        elif (situering.betreft_nummeraanduiding.__len__() == 14):
            landelijk_id = search_landelijk_id_nummeraanduiding(situering.betreft_nummeraanduiding)
            if landelijk_id:
                print('updating betreft_nummeraanduiding naar landelijk_id', landelijk_id[0])
                situering.betreft_nummeraanduiding = landelijk_id[0]
                situering.save()
            else:
                print('landelijk_id_not_found!')
        else:
            print('skip update betreft_nummeraanduiding, already has landelijk_id')