import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db import DatabaseError

import elasticsearch
import elasticsearch_dsl

try:
    # noinspection PyUnresolvedReferences
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

from django.http import HttpResponse

try:
    model = get_model(settings.HEALTH_MODEL)
except AttributeError:
    raise ImproperlyConfigured(
        'settings.HEALTH_MODEL {} doesn\'t resolve to '
        'a useable model'.format(settings.HEALTH_MODEL))


log = logging.getLogger(__name__)


def health(_request):
    """
    check database
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except DatabaseError:    # noqa
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain", status=500)

    # check elastic search
    try:
        client = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        es = elasticsearch_dsl.Search()
        es.using(client).query("match", all="x").execute()
    except AttributeError:
        message = "ELASTIC_SEARCH_HOSTS not in settings"
        log.exception(message)
        return HttpResponse(
            message,
            content_type="text/plain", status=500)
    except BaseException:
        message = "No elastic search server found on {}".format(settings.ELASTIC_SEARCH_HOSTS)
        log.exception(message)
        return HttpResponse(
            message,
            content_type="text/plain", status=500)

    return HttpResponse(
        "Connectivity OK", content_type='text/plain', status=200)


def check_data(request):

    if model.objects.all().count() < 3000:
        return HttpResponse(
            "Too few monumenten data in the database",
            content_type="text/plain", status=500)

    # check elastic
    try:
        client = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        x = elasticsearch_dsl.Search().using(client).index(settings.ELASTIC_INDICES['MONUMENTEN']).query(
            "match_all").execute()
        assert x.hits.total > 3000

    except elasticsearch.TransportError:
        log.exception("Too few monumenten data in ES database")
        return HttpResponse(
            "Autocomplete failed", content_type="text/plain", status=500)

    return HttpResponse(
        "Data OK", content_type='text/plain', status=200)
