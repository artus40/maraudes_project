from django.conf.urls import include, url

from django.contrib.auth import views as auth_views

from .views import Index, login_view
from maraudes import urls as maraudes_urls
from notes import urls as notes_urls
from utilisateurs import urls as utilisateurs_urls
from statistiques import urls as stats_urls

urlpatterns = [
    # Authentification
    url(r'^$', Index.as_view(), name="index"),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', auth_views.logout, {
                                'next_page': 'index',
                                }, name="logout"),
    # Applications
    url(r'^maraudes/', include(maraudes_urls, namespace="maraudes")),
    url(r'^notes/', include(notes_urls, namespace="notes")),
    url(r'^utilisateurs/', include(utilisateurs_urls, namespace="utilisateurs")),
    url(r'^statistiques/', include(stats_urls, namespace="statistiques")),
]
