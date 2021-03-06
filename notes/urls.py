from django.conf.urls import url

from . import views

app_name = "notes"

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'sujets/$', views.SujetListView.as_view(), name="liste-sujet"),
    url(r'sujets/(?P<pk>[0-9]+)/$', views.SuiviSujetView.as_view(), name="details-sujet"),
    url(r'sujets/(?P<pk>[0-9]+)/merge/$', views.MergeView.as_view(), name="sujets-merge"),
    url(r'maraudes/$', views.MaraudeListView.as_view(), name="liste-maraude"),
    url(r'maraudes/(?P<pk>[0-9]+)/$', views.CompteRenduDetailsView.as_view(), name="details-maraude"),
    # Manage Sujet
    url(r'sujets/create/$', views.SujetCreateView.as_view(), name="create-sujet"),
    url(r'sujet/(?P<pk>[0-9]+)/$', views.SujetAjaxDetailsView.as_view(), name="sujet"),
    url(r'sujet/(?P<pk>[0-9]+)/update/$', views.SujetAjaxUpdateView.as_view(), name="update-sujet"),
]
