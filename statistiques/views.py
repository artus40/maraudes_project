from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

from .actions import merge_two
from .models import *
from notes.forms import SelectSujetForm

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




class MergeView(generic.DetailView, generic.FormView):
    """ Implement actions.merge_two as a view """

    template_name = "statistiques/sujet_merge.html"
    model = FicheStatistique
    form_class = SelectSujetForm

    def form_valid(self, form):
        slave = self.get_object()
        master = form.cleaned_data['sujet']
        try:
            merge_two(master, slave)
        except:
            messages.error(self.request, "La fusion vers %s a échoué !" % master)
            return redirect(slave)
        messages.success(self.request, "%s vient d'être fusionné" % slave)
        return redirect(master)
