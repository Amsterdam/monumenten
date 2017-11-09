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
    naam = es.Text(fielddata=True, analyzer=analyzers.monument_naam,
                   fields={'raw': es.String(index='not_analyzed')})


class Complex(es.DocType):
    """
    Elastic data for Complex
    """
    id = es.Keyword(index='not_analyzed')
    naam = es.Text(fielddata=True, analyzer=analyzers.monument_naam,
                   fields={'raw': es.String(index='not_analyzed')})


def from_monument(mon: models.Monument):
    m = Monument(_id='{}'.format(mon.id))
    m.naam = mon.display_naam
    return m


def from_complex(comp: models.Complex):
    c = Complex(_id='{}'.format(comp.id))
    c.naam = comp.complexnaam
    return c
