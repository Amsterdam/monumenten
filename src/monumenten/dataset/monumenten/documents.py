import logging

import elasticsearch_dsl as es

from monumenten.dataset import models
from monumenten.dataset.generic import analyzers

log = logging.getLogger(__name__)


class Monument(es.DocType):
    """
    Elastic data for Monument
    """
    id = es.Keyword()
    type = es.Keyword()
    naam = es.Text(
        fielddata=True, analyzer=analyzers.monument_naam,
        fields={
            'raw': es.Text(fielddata=True),
            'keyword': es.Text(
                fielddata=True, analyzer=analyzers.subtype)})


def from_monument(mon: models.Monument):
    m = Monument(_id='{}'.format(mon.id))
    m.naam = mon.display_naam
    m.type = 'monument'
    return m


def from_complex(comp: models.Complex):
    #c = Monument(_id='c{}'.format(comp.id))
    c = Monument(_id='{}'.format(comp.id))
    c.naam = comp.complexnaam
    c.type = 'complex'
    return c
