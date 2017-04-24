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


class MonumentenRouter(routers.DefaultRouter):
    """
    De monumenten in de stad worden hier als een lijst getoond. Ze zijn
    tevens op te vragen vanuit Atlas
    """

    def get_api_root_view(self, **kwargs):
        # noinspection PyCompatibility
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Monumenten(cls):
            pass

        Monumenten.__doc__ = self.__doc__
        return Monumenten.as_view()


monumenten = MonumentenRouter()

monumenten.register(r'situeringen', api_views.SitueringList,
                    base_name='situeringen')
monumenten.register(r'monumenten', api_views.MonumentViewSet,
                    base_name='monumenten')
monumenten.register(r'complexen', api_views.ComplexViewSet,
                    base_name='complexen')

urls = monumenten.urls

