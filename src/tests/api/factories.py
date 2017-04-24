import random
from datetime import datetime, timedelta

import factory
from django.contrib.gis.geos import Point
from factory import fuzzy
from monumenten.dataset import models


def gen_janee():
    JANEE = 'nee'
    return JANEE


def create_testset(nr=10):
    point = Point(121944.32, 487722.88)

    for n0 in range(nr):
        _complex = ComplexFactory(id=n0, monumentnummer_complex=8392183)
        for n1 in range(5):
            pk = str(n0) + '-' + str(n1)
            monument = MonumentenDataFactory(
                complex=_complex,
                monumentcoordinaten=point,
                id=pk)

            for _ in range(5):
                SitueringFactory(monument=monument)


class SitueringFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Situering

    betreft_nummeraanduiding = fuzzy.FuzzyInteger(low=0)
    # situering_nummeraanduiding = models.CharField(length=128, null=True)
    eerste_situering = fuzzy.FuzzyAttribute(gen_janee)

    huisnummer = fuzzy.FuzzyInteger(low=1)
    if random.randint(0, 50) % 3 == 0:
        huisletter = fuzzy.FuzzyText(length=1)
    if random.randint(0, 50) % 3 == 0:
        huisnummertoevoeging = fuzzy.FuzzyText(length=4)
    postcode = fuzzy.FuzzyText(length=6)
    straat = fuzzy.FuzzyText(length=80)


class MonumentenDataFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Monument

    if random.randint(0, 50) % 3 == 0:  # one in 3 is filled
        monument_aanwijzingsdatum = fuzzy.FuzzyDate(
            start_date=datetime.today() - timedelta(
                days=random.randint(10, 9000)), end_date=datetime.today())
    architect_ontwerp_monument = fuzzy.FuzzyText(length=128)
    if random.randint(0, 50) % 3 == 0:
        heeft_als_grondslag_beperking = fuzzy.FuzzyInteger(low=0)
    beschrijving_monument = fuzzy.FuzzyText()
    monumentcoordinaten = fuzzy.FuzzyInteger(low=1)
    oorspronkelijke_functie_monument = fuzzy.FuzzyText(length=128)
    in_onderzoek = fuzzy.FuzzyText(length=3)
    monumentnummer = factory.sequence(lambda n: n)
    monumentnaam = fuzzy.FuzzyText(length=255)
    monumentnaam = fuzzy.FuzzyText(length=255)
    opdrachtgever_bouw_monument = fuzzy.FuzzyText(length=128)
    betreft_pand = factory.sequence(lambda n: n)
    if random.randint(0, 50) % 4:
        redengevende_omschrijving_monument = fuzzy.FuzzyText()
    if random.randint(0, 50) % 4:
        monumentstatus = fuzzy.FuzzyText(length=128)
    monumenttype = fuzzy.FuzzyText(length=128)


class ComplexFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Complex
    external_id = fuzzy.FuzzyText(length=36)

    beschrijving_complex = fuzzy.FuzzyText()
    monumentnummer_complex = factory.sequence(lambda n: n)
    complexnaam = fuzzy.FuzzyText(length=255)
    complexstatus = fuzzy.FuzzyText(length=128)
