from django.conf.urls import url

from . import views
from sujets import views as sujets_views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'(?P<pk>[0-9]+)/$', views.SuiviSujetView.as_view(), name="details"),
]
