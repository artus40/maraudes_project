from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<pk>[0-9]+)/$', views.SujetDetailsView.as_view(), name="details"),
    url(r'(?P<pk>[0-9]+)/update/$', views.SujetUpdateView.as_view(), name="update"),
    url(r'create/$', views.SujetCreateView.as_view(), name="create"),
]
