"""monumenten URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import response, schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

from monumenten.api import urls as api_urls

grouped_url_patterns = {
    'base_patterns': [
        url(r'^status/', include('monumenten.health.urls')),
    ],
    'monumenten_patterns': [
        url(r'^monumenten/', include(api_urls.urls)),
    ],
}


@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
def monumenten_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Monumenten lists',
        patterns=grouped_url_patterns['monumenten_patterns']
    )
    return response.Response(generator.get_schema(request=request))


urlpatterns = [url('^monumenten/docs/api-docs/monumenten/$',
                   monumenten_schema_view),
               ] + [url for pattern_list in grouped_url_patterns.values()
                    for url in pattern_list]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
