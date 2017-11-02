import logging

import elasticsearch_dsl as es

from monumenten.dataset import models
from monumenten.dataset.generic import analyzers

log = logging.getLogger(__name__)


class Monument(es.DocType):
    """
    Elastic data for Monument
    """
    id = es.Keyword(index='not_analyzed')
    display_naam = es.Text(fielddata=True, analyzer=analyzers.display_naam)


class Complex(es.DocType):
    """
    Elastic data for Complex
    """
    id = es.Keyword(index='not_analyzed')
    complexnaam = es.Text(fielddata=True, analyzer=analyzers.naam)


def from_monument(mon: models.Monument):
    m = Monument(_id='{}'.format(mon.id))
    m.display_naam = mon.display_naam
    return m


def from_complex(comp: models.Complex):
    c = Complex(_id='{}'.format(comp.id))
    c.complexnaam = comp.complexnaam
    return c
