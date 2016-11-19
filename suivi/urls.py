from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'liste/$', views.SujetListView.as_view(), name="liste"),
    url(r'(?P<pk>[0-9]+)/$', views.SuiviSujetView.as_view(), name="details"),
]
