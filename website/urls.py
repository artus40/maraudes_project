from django.conf.urls import include, url

from django.contrib.auth import logout as logout_view

from .views import Index, login_view

urlpatterns = [
    # Authentification
    url(r'^$', Index.as_view(), name="index"),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, {
                                'next_page': 'index',
                                }, name="logout"),
    # Applications
    url(r'^maraudes/', include('maraudes.urls', namespace="maraudes")),
    url(r'^notes/', include('notes.urls', namespace="notes")),
    url(r'^utilisateurs/', include('utilisateurs.urls', namespace="utilisateurs")),
    url(r'^statistiques/', include('statistiques.urls', namespace="statistiques")),
]
