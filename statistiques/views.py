from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

from .models import FicheStatistique
from .forms import StatistiquesForm

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


# AjaxMixin

class AjaxOrRedirectMixin:
    """ For view that should be retrieved by Ajax only. If not,
        redirects to the primary view where these are displayed """

    def get(self, *args, **kwargs):
        """ Redirect to complete details view if request is not ajax """
        if not self.request.is_ajax():
            return redirect("notes:details-sujet", pk=self.get_object().pk)
        return super().get(*args, **kwargs)

class StatistiquesDetailsView(AjaxOrRedirectMixin, generic.DetailView):

    model = FicheStatistique
    template_name = "statistiques/details.html"



class StatistiquesUpdateView(AjaxOrRedirectMixin, generic.UpdateView):

    model = FicheStatistique
    form_class = StatistiquesForm
    template_name = "statistiques/update.html"
