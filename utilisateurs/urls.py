from django.conf.urls import url

from . import views

app_name = "utilisateurs"

urlpatterns = [
    url(r'^$', views.UtilisateurView.as_view(), name="index"),
]
