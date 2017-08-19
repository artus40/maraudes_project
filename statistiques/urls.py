from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.DashboardView.as_view(), name="index"),
    url('^charts/$', views.TypologieChartsView.as_view(), name="typologie"),
    url(r'^details/(?P<pk>[0-9]+)/$', views.StatistiquesDetailsView.as_view(), name="details"),
    url(r'^update/(?P<pk>[0-9]+)/$', views.StatistiquesUpdateView.as_view(), name="update"),
    url(r'^frequentation/$', views.FrequentationChartsView.as_view(), name="frequentation"),
]
