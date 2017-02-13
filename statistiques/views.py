from django.shortcuts import render
from django.views import generic
# Create your views here.
from .apps import stats

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

@stats.using(title=('Statistiques', 'accueil'))
class IndexView(generic.TemplateView):

    template_name = "statistiques/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        data_source = SimpleDataSource(data= [
            ['Mois', 'Nbr de rencontres'],
            [1, 12],
            [2, 14],
            [3, 9],
        ])
        context['chart'] = flot.LineChart(data_source)
        return context
