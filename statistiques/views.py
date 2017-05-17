from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic
from django.db.models import (Field, CharField, NullBooleanField,
                              Count,
                              )

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import gchart

from .models import FicheStatistique
from .forms import StatistiquesForm, SelectRangeForm
from .charts import PieWrapper

from maraudes.notes import Observation
from notes.models import Sujet

class FilterMixin(generic.edit.FormMixin):

    form_class = SelectRangeForm

    def get_initial(self):
        return {'month': self.request.GET.get('month', 0), 'year': self.request.GET.get('year', 0) }

    def get(self, *args, **kwargs):
        self.year = int(self.request.GET.get('year', 0))
        self.month = int(self.request.GET.get('month', 0))
        return super().get(self, *args, **kwargs)


class DashboardView(generic.TemplateView):
    template_name = "statistiques/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)



        return context


class PieChartView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/typologie.html"

    def get_queryset(self, model=FicheStatistique):
        month = self.month
        year = self.year
        qs = model.objects.all()
        if month and year:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__year=year, created_date__month=month).values_list('sujet'))
        elif year:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__year=year).values_list('sujet'))
        elif month:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__month=month).values_list('sujet'))
        return qs

    def get_graphs(self):
        sujets = self.get_queryset(model=Sujet)
        # Insertion des champs 'âge' et 'genre' du modèle notes.Sujet
        for field in Sujet._meta.fields:
            if field.name == 'genre':
                yield str(field.verbose_name), PieWrapper(sujets, field)
            if field.name == 'age':
                categories = (
                    ('Mineurs', range(0,18)),
                    ('18-24', range(18,25)),
                    ('25-34', range(25,35)),
                    ('35-44', range(35,45)),
                    ('45-54', range(45,55)),
                    ('+ de 55', range(55,110)),
                )
                nbr_sujets = lambda rg: sujets.filter(age__in=rg).count()

                yield "Âge", PieWrapper(
                                data=[("age", "count")] +
                                    [(label, nbr_sujets(rg))
                                    for label, rg in categories] +
                                    [("Ne sait pas", sujets.filter(age=None).count())],
                                title="Âge des sujets")

        # Puis des champs du modèle statistiques.FicheStatistique
        # dans leur ordre de déclaration
        queryset = self.get_queryset()
        for field in FicheStatistique._meta.fields:
            if field.__class__ in (NullBooleanField, CharField):
                yield str(field.verbose_name), PieWrapper(queryset, field)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['graphs'] = [(title, graph) for title, graph in self.get_graphs()]
        context['queryset'] = self.get_queryset()
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
    template_name = "statistiques/fiche_stats_details.html"



class StatistiquesUpdateView(AjaxOrRedirectMixin, generic.UpdateView):

    model = FicheStatistique
    form_class = StatistiquesForm
    template_name = "statistiques/fiche_stats_update.html"
