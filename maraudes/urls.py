# Maraudes URLconf

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'planning/$', views.PlanningView.as_view(), name="planning"),
    url(r'liste/$', views.MaraudeListView.as_view(), name="liste"),
    url(r'lieu/create/$', views.LieuCreateView.as_view(), name="lieu-create"),
    # Compte-rendus de maraude
    url(r'^(?P<pk>[0-9]+)/$', views.MaraudeDetailsView.as_view(), name="details"),
    url(r'^(?P<pk>[0-9]+)/update/$', views.CompteRenduUpdateView.as_view(), name="update"),
    url(r'^(?P<pk>[0-9]+)/cr/$', views.CompteRenduCreateView.as_view(), name="create"),
]
