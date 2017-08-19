from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views import generic
from django.db.models import (CharField, NullBooleanField)

from maraudes.notes import Observation
from maraudes.models import Maraude, HORAIRES_APRESMIDI, HORAIRES_SOIREE
from notes.models import Sujet

from .models import FicheStatistique
from .forms import StatistiquesForm, SelectRangeForm
from . import charts
###

NO_DATA = "Aucune donnée"


class FilterMixin(generic.edit.FormView):

    form_class = SelectRangeForm
    request = None
    year = None

    def get_initial(self):
        return {
                'period': self.year,
                }

    def parse_args(self, request):
        period = request.GET.get("period", "0")
        self.year = int(period)

    def get(self, request, *args, **kwargs):
        self.parse_args(request)
        return super().get(self, *args, **kwargs)

    def _filters(self, prefix):
        return {'%s__%s' % (prefix, attr): getattr(self, attr) for attr in ('year',)
                if getattr(self, attr) > 0}

    def get_observations_queryset(self):
        return Observation.objects.filter(**self._filters('created_date'))

    def get_maraudes_queryset(self):
        return Maraude.objects.filter(**self._filters('date'))

    def get_fichestatistiques_queryset(self):
        return FicheStatistique.objects.filter(pk__in=self.get_sujets_queryset().values_list('pk'))

    def get_sujets_queryset(self, selection=None):
        if not selection:
            selection = self.get_observations_queryset()
        return Sujet.objects.filter(pk__in=selection.values_list('sujet'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.year
        return context


class MultipleChartsView(FilterMixin, generic.TemplateView):

    title = None
    description = None
    _charts = {}  # Set of charts managed by the view

    _active = None  # Name of the active chart
    _chart = None  # Active chart object
    template_name = "statistiques/multiple_charts.html"

    def __init__(self, **kwargs):
        if not self._charts:
            raise ImproperlyConfigured()
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self._active = request.GET.get('graph', None)
        if self._active:
            self._chart = self._charts.get(self._active, None)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """ Returns the queryset of objects used to draw graphs """
        raise NotImplementedError("Subclass must implement this method")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = str(self.title)
        context['chart_list'] = list(self._charts.keys())
        context['active'] = self._active
        if self._chart:  # Need to instantiate the chart
            queryset = self.get_queryset()
            context['queryset_count'] = queryset.count()
            context['chart'] = self._chart(queryset)
        return context


class DashboardView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        maraudes = self.get_maraudes_queryset()
        rencontres = self.get_observations_queryset()

        context['chart'] = charts.DonneeGeneraleChart(
                                maraudes=(maraudes,
                                          maraudes.filter(heure_debut=HORAIRES_APRESMIDI),
                                          maraudes.filter(heure_debut=HORAIRES_SOIREE)
                                          ),
                                rencontres=(rencontres,
                                            rencontres.filter(rencontre__maraude__heure_debut=HORAIRES_APRESMIDI),
                                            rencontres.filter(rencontre__maraude__heure_debut=HORAIRES_SOIREE)),
                                )

        return context


class TypologieChartsView(MultipleChartsView):
    title = "Typologie"

    _charts = OrderedDict(
        [('Âge', charts.AgePieChart),
         ('Genre', charts.GenrePieChart),
         ] +
        [(f.verbose_name, charts.generate_piechart_for_field(f)) for f in FicheStatistique._meta.get_fields()
         if f.__class__ in (NullBooleanField, CharField)
         ]
    )

    def get_queryset(self):
        return self.get_fichestatistiques_queryset()


class FrequentationChartsView(MultipleChartsView):
    title = "Fréquentation"
    _charts = OrderedDict([
        ('Par mois', charts.RencontreParMoisChart),
        ('Par heure', charts.RencontreParHeureChart),
        ('Par sujet', charts.RencontreParSujetChart),
        ])

    def get_queryset(self):
        return self.get_observations_queryset()


# AjaxMixin
class AjaxOrRedirectMixin(generic.DetailView):
    """ For view that should be retrieved by Ajax only. If not,
        redirects to the primary view where these are displayed """

    def get(self, *args, **kwargs):
        """ Redirect to complete details view if request is not ajax """
        if not self.request.is_ajax():
            return redirect("notes:details-sujet", pk=self.get_object().pk)
        return super().get(*args, **kwargs)


class StatistiquesDetailsView(AjaxOrRedirectMixin):

    model = FicheStatistique
    template_name = "statistiques/fiche_stats_details.html"


class StatistiquesUpdateView(AjaxOrRedirectMixin):

    model = FicheStatistique
    form_class = StatistiquesForm
    template_name = "statistiques/fiche_stats_update.html"
