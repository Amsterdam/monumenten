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
from django.conf.urls import url, include
from django.conf import settings
import monumenten.health.views
from monumenten.api import views

urlpatterns = [
    url(r'^status/health$', monumenten.health.views.health),
    url(r'^status/data$', monumenten.health.views.check_data),
    url(r'^monumenten/monument/$', views.MonumentList.as_view(), name='monumenten-list'),
    url(r'^monumenten/monument/([0-9]+)/$', views.MonumentDetail.as_view(), name='monumenten-detail'),
    url(r'^monumenten/monument/([0-9]+)/situering/$', views.SitueringList.as_view(), name='situering-list'),
    url(r'^monumenten/situering/([0-9]+)/$', views.SitueringDetail.as_view(), name='situering-detail'),

]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
