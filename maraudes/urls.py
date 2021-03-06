# Maraudes URLconf

from django.conf.urls import url

from . import views

app_name = "maraudes"

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^compte-rendu$', views.redirect_to_current_compterendu, name="cr-link"),
    url(r'^planning/$', views.PlanningView.as_view(), name="planning"),
    url(r'^lieu/create/$', views.LieuCreateView.as_view(), name="lieu-create"),
    url(r'^(?P<pk>[0-9]+)/create/$', views.CompteRenduCreateView.as_view(), name="create"),
    url(r'^(?P<pk>[0-9]+)/finalize/$', views.FinalizeView.as_view(), name="finalize"),
]
