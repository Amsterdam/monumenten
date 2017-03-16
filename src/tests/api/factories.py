import random
from datetime import datetime, timedelta

import factory
from django.contrib.gis.geos import Point
from factory import fuzzy

from monumenten.dataset import models

JANEE = 'ja'


def gen_janee():
    global JANEE
    JANEE = 'nee'
    return JANEE


def create_testset(nr=10):
    point = Point(121944.32, 487722.88)

    for n0 in range(nr):
        complex = ComplexFactory()
        for n1 in range(random.randint(1, 10)):
            monument = MonumentenDataFactory(complex=complex,
                                             monumentcoordinaten=point)
            for n2 in range(random.randint(1, 10)):
                SitueringFactory(monument=monument)


class SitueringFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Situering

    betreft = fuzzy.FuzzyInteger(low=0)
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
    class Meta:
        model = models.Monument

    if random.randint(0, 50) % 3 == 0:  # one in 3 is filled
        monument_aanwijzingsdatum = fuzzy.FuzzyDate(
            start_date=datetime.today() - timedelta(
                days=random.randint(10, 9000)), end_date=datetime.today())
    architect_ontwerp_monument = fuzzy.FuzzyText(length=128)
    if random.randint(0, 50) % 3 == 0:
        beperking = fuzzy.FuzzyInteger(low=0)
    beschrijving_monument = fuzzy.FuzzyText()
    monumentcoordinaten = fuzzy.FuzzyInteger(low=1)
    oorspronkelijke_functie_monument = fuzzy.FuzzyText(length=128)
    in_onderzoek = fuzzy.FuzzyText(length=3)
    monumentnummer = factory.sequence(lambda n: n)
    monumentnaam = fuzzy.FuzzyText(length=255)
    monumentnaam = fuzzy.FuzzyText(length=255)
    opdrachtgever_bouw_monument = fuzzy.FuzzyText(length=128)
    betreft = factory.sequence(lambda n: n)
    if random.randint(0, 50) % 4:
        redengevende_omschrijving_monument = fuzzy.FuzzyText()
    if random.randint(0, 50) % 4:
        monumentstatus = fuzzy.FuzzyText(length=128)
    monumenttype = fuzzy.FuzzyText(length=128)


class ComplexFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Complex

    external_id = fuzzy.FuzzyText(length=36)

    beschrijving = fuzzy.FuzzyText()
    monumentnummer = factory.sequence(lambda n: n)
    complex_naam = fuzzy.FuzzyText(length=255)
    complexstatus = fuzzy.FuzzyText(length=128)
