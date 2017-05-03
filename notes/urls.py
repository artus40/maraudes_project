from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'sujets/$', views.SujetListView.as_view(), name="liste-sujet"),
    url(r'sujets/(?P<pk>[0-9]+)/$', views.SuiviSujetView.as_view(), name="details-sujet"),
    url(r'maraudes/$', views.MaraudeListView.as_view(), name="liste-maraude"),
    url(r'maraudes/(?P<pk>[0-9]+)/$', views.MaraudeDetailsView.as_view(), name="details-maraude"),
    # Manage Sujet
    url(r'sujet/(?P<pk>[0-9]+)/$', views.SujetDetailsView.as_view(), name="details-sujet"),
    url(r'sujet/(?P<pk>[0-9]+)/update/$', views.SujetUpdateView.as_view(), name="update-sujet"),
    url(r'sujet/create/$', views.SujetCreateView.as_view(), name="create-sujet"),
]
