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

class FilterMixin(generic.edit.FormMixin):

    form_class = SelectRangeForm

    def get_initial(self):
        return {'month': self.request.GET.get('month', 0), 'year': self.request.GET.get('year', 0) }

    def get_queryset(self):
        month = int(self.request.GET.get('month', 0))
        year = int(self.request.GET.get('year', 0))
        qs = FicheStatistique.objects.all()
        if month and year:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__year=year, created_date__month=month).values_list('sujet'))
        elif year:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__year=year).values_list('sujet'))
        elif month:
            qs = qs.filter(pk__in=Observation.objects.filter(created_date__month=month).values_list('sujet'))
        return qs



class DashboardView(generic.TemplateView):
    template_name = "statistiques/index.html"



class PieChartView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/camemberts.html"

    def get_graphs(self):
        queryset = self.get_queryset()
        for field in FicheStatistique._meta.fields:
            if field.__class__ in (NullBooleanField, CharField):
                yield "%s" % field.verbose_name, PieWrapper(
                    queryset, field,
                )

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
    template_name = "statistiques/details.html"



class StatistiquesUpdateView(AjaxOrRedirectMixin, generic.UpdateView):

    model = FicheStatistique
    form_class = StatistiquesForm
    template_name = "statistiques/update.html"
