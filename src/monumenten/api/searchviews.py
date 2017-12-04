# Create your views here.
from collections import OrderedDict

from rest_framework.compat import coreapi, coreschema
from django.conf import settings
from django.utils.encoding import force_text

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch, Q
from elasticsearch.exceptions import TransportError

from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

import logging

from monumenten.dataset.generic.queries import ElasticQueryWrapper

log = logging.getLogger(__name__)

MONUMENTEN = settings.ELASTIC_INDICES['MONUMENTEN']


_details = {
    'monument': 'monumenten-detail',
    'complex': 'complexen-detail',
}


def get_url(request, hit):
    """
    Get a detail API url for hit
    """
    doc_type, doc_id = hit.meta.doc_type, hit.meta.id

    if doc_type in _details:
        return OrderedDict([
            ('self', dict(
                href=reverse(_details[doc_type], kwargs=dict(pk=doc_id), request=request)
            ))
        ])


def multimatch_complexen_monumenten_q(query):
    return {
        'bool': {
            'should': [
                {
                    'constant_score': {
                        'query': {
                            'prefix': {
                                'naam.keyword': query,
                            }
                        },
                        'boost': 10,
                    },
                },
                {
                    'constant_score': {
                        'query': {
                            'multi_match': {
                                'query': query,
                                'type': 'phrase_prefix',
                                'max_expansions': 100,
                                'fields': [
                                    'naam',
                                ]
                            }
                        },
                        'boost': 5,
                    }
                }
            ],
            'minimum_should_match': 1,
        }
    }


def multimatch_complexen_monumenten_q_wrapper(query) -> ElasticQueryWrapper:
    """
    Basis openbare-ruimte query.

    Het resultaat ordent pure prefix matches vóór phrase_prefix matches.
    """

    # Logica:
    # Het doel is om 'echte' prefix-matches te sorteren vóór phrase-prefix
    # matches.  Met alleen phrase-prefix kan dat niet, dus we gebruiken twee
    # 'should' queries waarvan er minimaal één moet matchen. Met de
    # constant_score wrapper zorgen we ervoor dat alle 'prefix' matches een
    # score van 10 krijgen, en alle 'phrase_prefix' matches een score van 5.
    # De 'constant_score' op de 'must' voorkomt dat die in de weg zit.  Op
    # basis van deze output kunnen we vervolgens ordenen op score, gevolgd
    # door naam.
    #
    # Voorbeelden: Zoeken op hort, geeft eerst Hortus Botanicus, dan pas BRUG 232, HORTUS
    log.debug('%20s %s', multimatch_complexen_monumenten_q_wrapper.__name__, query)

    sort_fields = ['_score', 'naam.keyword']

    return ElasticQueryWrapper(
        query=multimatch_complexen_monumenten_q(query),
        indexes=[MONUMENTEN],
        sort_fields=sort_fields,
        size=50,
    )


def search_complexen_monumenten_query(view, client, query):
    """
    Execute search on adresses
    """
    return multimatch_complexen_monumenten_q_wrapper(query).to_elasticsearch_object(client)


class QueryMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            q=dict(
                type="string",
                description="The query to search for",
                required=False
            )
        )
        return result


def multimatch_q(query):
    """
    main 'One size fits all' search query used
    """
    log.debug('%20s %s', multimatch_q.__name__, query)

    return Q(
        "multi_match",
        query=query,
        type="phrase_prefix",
        max_expansions=100,
        fields=[
            "naam"
        ]
    )


def default_search_query(client, query: str):
    """
    Execute search.

    ./manage.py test monumenten.api.tests.test_query --keepdb

    """

    return (
        Search()
        .using(client)
        .query(
            multimatch_q(query)
        )
        .sort("naam.raw")
    )


class QFilter(object):
    """
    For openapi documentation purposes
    return the q field
    """
    search_title = 'search title'
    search_description = 'search description'

    def get_schema_fields(self, _view):
        """
        return Q parameter documentation
        """
        return [
            coreapi.Field(
                name='q',
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]


class QSearchFilter(QFilter):
    search_description = 'Search complexen/monumenten'
    search_title = 'Complex/monument'


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects
    that match the elastic search query.

    *NOTE*

    We assume the input is correct but could be incomplete

    for example: seaching for a not existing
    Rozengracht 3 will return Rozengracht 3-1 which does exist
    """

    metadata_class = QueryMetadata
    page_size = 100
    search_query = default_search_query
    url_name = 'search-list'

    def _set_followup_url(self, request, result, end,
                          response, query, page):
        """
        Add pageing links for result set to response object
        """

        followup_url = reverse(self.url_name, request=request)

        if page == 1:
            prev_page = None
        elif page == 2:
            prev_page = "{}?q={}".format(followup_url, query)
        else:
            prev_page = "{}?q={}&page={}".format(followup_url, query, page - 1)

        total = result.hits.total

        if end >= total:
            next_page = None
        else:
            next_page = "{}?q={}&page={}".format(followup_url, query, page + 1)

        response['_links'] = OrderedDict([
            ('self', dict(href=followup_url)),
        ])

        if next_page:
            response['_links']['next'] = dict(href=next_page)
        else:
            response['_links']['next'] = None

        if prev_page:
            response['_links']['previous'] = dict(href=prev_page)
        else:
            response['_links']['previous'] = None

    def list(self, request, *args, **kwargs):

        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            page = int(request.query_params['page'])

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']
        query = query.lower()

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, query)[start:end]

        try:
            result = search.execute()
        except TransportError:
            log.exception("Could not execute search query " + query)
            return Response([])

        response = OrderedDict()

        # self._set_followup_url(request, result, end, response, query, page)
        # import pdb; pdb.set_trace()

        response['count'] = result.hits.total

        self.create_summary_aggregations(request, result, response)

        response['results'] = [
            self.normalize_hit(h, request) for h in result.hits]

        return Response(response)

    def create_summary_aggregations(self, request, result, response):
        """
        If there are aggregations within the search result.
        show them
        """
        # do noting yet

        return

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['_links'] = get_url(request, hit)

        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index

        if result['type'] == 'complex':
            name_extension = ' (complex)'
        else:
            name_extension = ''

        hit_dict = hit.to_dict()
        hit_dict['_display'] = hit_dict['naam'] + name_extension
        del hit_dict['naam']
        result.update(hit_dict)

        return result

    def normalize_bucket(self, field, request):
        # print(field)
        result = OrderedDict()
        result.update(field.to_dict())
        return result


class SearchComplexenMonumentenViewSet(SearchViewSet):
    """
    Zoek-Monumenten

    Given a query parameter `q`, this function returns a subset of
    all monument objects that match the naam elastic search query.

    """
    metadata_class = QueryMetadata
    url_name = 'search/monumenten'
    search_query = search_complexen_monumenten_query
    filter_backends = [QSearchFilter]


def autocomplete_query(client, query):
    """
    :return: Ordered sets of responses for monuments and complexes closest to the requested query
    """

    return (MultiSearch().using(client).index(MONUMENTEN).add(Search().doc_type("monument").query(
            multimatch_complexen_monumenten_q(query)).sort('_score', 'naam.raw')[0:3]).add(
        Search().doc_type("complex").query(
            multimatch_complexen_monumenten_q(query)).sort('_score', 'naam.raw')[0:3]))


def get_autocomplete_response(client, query):
    results = autocomplete_query(client, query).execute()

    content = []
    for result in results:
        for hit in result.hits:
            if hit.meta.doc_type == 'complex':
                uri_part = 'complexen'
                name = 'naam'
                name_extension = ' (complex)'
            else:
                uri_part = 'monumenten'
                name = 'naam'
                name_extension = ''

            content.append({
                '_display': '{v}{e}'.format(v=hit[name], e=name_extension),
                'uri': 'monumenten/{u}/{v}/'.format(u=uri_part, v=hit.meta.id)
            })

    return [{
        'label': 'Monumenten',
        'content': content
    }]


class QTypeAheadFilter(QFilter):
    search_description = 'Autocomplete complexen/monumenten'
    search_title = 'Complex/monument'


class TypeaheadViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a
    subset of all objects
    that (partially) match the specified query.

    *NOTE*

    We assume spelling errors and therefore it is possible
    to have unexpected results

    Autocomplete monumenten
    """

    filter_backends = [QTypeAheadFilter]

    def get_autocomplete_response(self, client, query):
        return get_autocomplete_response(client, query)

    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q'].strip().lower()

        if len(query) < 3:
            return Response([])

        response = self.get_autocomplete_response(self.client, query)
        return Response(response)
