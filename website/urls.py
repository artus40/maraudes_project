from django.conf.urls import include, url

from django.contrib.auth import views as auth_views

from .views import Index
from maraudes import urls as maraudes_urls
from suivi import urls as suivi_urls
from sujets import urls as sujets_urls

urlpatterns = [
    url('^$', Index.as_view(), name="index"),
    # Applications
    url(r'^maraudes/', include(maraudes_urls, namespace="maraudes")),
    url(r'^suivi/', include(suivi_urls, namespace="suivi")),
    url(r'^sujets/', include(sujets_urls, namespace="sujets")),
    # Authentification
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name="login"),
    url(r'^logout/$', auth_views.logout, {
                                'template_name': 'logout.html',
                                'next_page': 'login',
                                }, name="logout"),
]
