import logging

import elasticsearch_dsl as es

from monumenten import settings
from monumenten.dataset import models
from monumenten.dataset.generic import analyzers

log = logging.getLogger(__name__)


class Monument(es.Document):
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

    class Index:
        name = settings.ELASTIC_INDICES['MONUMENTEN']


def from_monument(mon: models.Monument):
    m = Monument(_id='{}'.format(mon.id))
    m.naam = mon.display_naam
    m.type = 'monument'
    return m


def from_complex(comp: models.Complex):
    c = Monument(_id='{}'.format(comp.id))
    c.naam = comp.complexnaam
    c.type = 'complex'
    return c
