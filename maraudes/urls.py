# Maraudes URLconf

from django.urls import path 

from . import views

app_name = "maraudes"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('compte-rendu', views.redirect_to_current_compterendu, name="cr-link"),
    path('planning/', views.PlanningView.as_view(), name="planning"),
    path('lieu/create/', views.LieuCreateView.as_view(), name="lieu-create"),
    path('<int:pk>/create/', views.CompteRenduCreateView.as_view(), name="create"),
    path('<int:pk>/finalize/', views.FinalizeView.as_view(), name="finalize"),
]
