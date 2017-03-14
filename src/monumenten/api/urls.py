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
from rest_framework import routers

from monumenten.api import views as api_views
from monumenten.health import views as health_views


class MonumentenRouter(routers.DefaultRouter):
    """
    De monumenten in de stad worden hier als een lijst getoond. Ze zijn tevens op
    te vragen vanuit Atlas
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Monumenten(cls):
            pass

        Monumenten.__doc__ = self.__doc__
        return Monumenten.as_view()


monumenten = MonumentenRouter()

monumenten.register(r'^status/health$', health_views.health, base_name='health')
monumenten.register(r'^status/data$', health_views.check_data, base_name='data')
monumenten.register(r'situeringen', api_views.SitueringList,
                    base_name='situering-list')
monumenten.register(r'monument', api_views.MonumentDetail,
                    base_name='monumenten-detail')
monumenten.register(r'monumenten', api_views.MonumentViewSet,
                    base_name='monumenten-list')
# monumenten.register(r'^monumenten/situering/([0-9]+)/$',
#                     api_views.SitueringDetail.as_view())
# urlpatterns = [
#     url(r'^', include(router.urls)),
#     url(r'^monumenten/docs', schema_view, name='docs'),
#     url(r'^status/health$', health_views.health),
#     url(r'^status/data$', health_views.check_data),
#     url(r'^monumenten/monument/$', api_views.MonumentList.as_view(),
#         name='monumenten-list'),
#     url(r'^monumenten/monument/([0-9]+)/$', api_views.MonumentDetail.as_view(),
#         name='monumenten-detail'),
#     url(r'^monumenten/monument/(?P<pand_id>[0-9]\w+)/$', api_views.MonumentPand.as_view(),
#         name='monumenten-pand'),
#     url(r'^monumenten/monument/([0-9]+)/situering/$',
#         api_views.SitueringList.as_view(), name='situering-list'),
#     url(r'^monumenten/situering/([0-9]+)/$',
#         api_views.SitueringDetail.as_view(),
#         name='situering-detail')
# ]
#
# if settings.DEBUG:
#     import debug_toolbar
#
#     urlpatterns.extend([
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#         url(r'^explorer/', include('explorer.urls')),
#     ])
