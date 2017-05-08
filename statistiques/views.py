from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

from .models import FicheStatistique

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

class StatistiquesDetailsView(generic.DetailView):

    model = FicheStatistique
    template_name = "statistiques/details.html"

class StatistiquesUpdateView(generic.UpdateView):

    model = FicheStatistique
    template_name = "statistiques/update.html"
    fields = "__all__"

