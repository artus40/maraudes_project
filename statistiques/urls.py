from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.IndexView.as_view(), name="index"),
    url(r'sujet/(?P<pk>[0-9]+)/merge/$', views.MergeView.as_view(), name="merge"),
]

