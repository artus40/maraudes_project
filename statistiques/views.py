from django.shortcuts import render
from django.views import generic
# Create your views here.
from .apps import stats

@stats.using(title=('Statistiques', 'accueil'))
class IndexView(generic.TemplateView):

    template_name = "statistiques/index.html"

