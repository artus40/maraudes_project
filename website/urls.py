from django.conf.urls import include, url

from django.contrib.auth import views as auth_views

from .views import Index, login_view
from maraudes import urls as maraudes_urls
from suivi import urls as suivi_urls
from sujets import urls as sujets_urls
from utilisateurs import urls as utilisateurs_urls

urlpatterns = [
    # Authentification
    url(r'^$', Index.as_view(), name="index"),
    url(r'^login/$', login_view),
    url(r'^logout/$', auth_views.logout, {
                                'template_name': 'logout.html',
                                'next_page': 'index',
                                }, name="logout"),
    # Applications
    url(r'^maraudes/', include(maraudes_urls, namespace="maraudes")),
    url(r'^suivi/', include(suivi_urls, namespace="suivi")),
    url(r'^sujets/', include(sujets_urls, namespace="sujets")),
    url(r'^utilisateurs/', include(utilisateurs_urls, namespace="utilisateurs")),
]
