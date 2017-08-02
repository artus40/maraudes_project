import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic
from django.db.models import (Field, CharField, NullBooleanField,
                              Count,
                              )
from django.db.models.functions.datetime import ExtractMonth
from graphos.sources.simple import SimpleDataSource
from graphos.renderers import gchart

from .models import FicheStatistique
from .forms import StatistiquesForm, SelectRangeForm
from .charts import PieWrapper, ColumnWrapper

from maraudes.notes import Observation
from maraudes.models import Maraude
from notes.models import Sujet

###


nom_mois = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre"
}


class FilterMixin(generic.edit.FormMixin):

    form_class = SelectRangeForm

    def get_initial(self):
        return {'month': self.request.GET.get('month', 0), 'year': self.request.GET.get('year', 0) }

    def get(self, *args, **kwargs):
        self.year = int(self.request.GET.get('year', 0))
        self.month = int(self.request.GET.get('month', 0))
        return super().get(self, *args, **kwargs)

    def _filters(self, prefix):
        return {'%s__%s' % (prefix, attr): getattr(self, attr) for attr in ('year', 'month')
                if getattr(self, attr) > 0 }

    def get_observations_queryset(self):
        return Observation.objects.filter(**self._filters('created_date'))

    def get_maraudes_queryset(self):
        return Maraude.objects.filter(**self._filters('date'))

    def get_fichestatistiques_queryset(self):
        return FicheStatistique.objects.filter(pk__in=self.get_observations_queryset().values_list('sujet'))

    def get_sujets_queryset(self):
        return Sujet.objects.filter(pk__in=self.get_observations_queryset().values_list('sujet'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.year
        context['month'] = self.month
        return context


NO_DATA = "Aucune donnée"

class DashboardView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        maraudes = self.get_maraudes_queryset()
        rencontres = self.get_observations_queryset()

        context['nbr_maraudes'] = maraudes.count() or NO_DATA
        context['nbr_maraudes_jour'] = maraudes.filter(
                                                    heure_debut=datetime.time(16,00)
                                                ).count() or NO_DATA
        context['nbr_rencontres'] = rencontres.count() or NO_DATA
        try:
            context['moy_rencontres'] = int(context['nbr_rencontres'] / context['nbr_maraudes'])
        except (ZeroDivisionError, TypeError):
            context['moy_rencontres'] = NO_DATA

        if self.year and not self.month: #Show rencontres_par_mois graph
            par_mois = rencontres.order_by().annotate(
                                            mois=ExtractMonth('created_date')
                                        ).values(
                                            'mois'
                                        ).annotate(
                                            nbr=Count('pk')
                                        )
            context['rencontres_par_mois'] = ColumnWrapper(
                SimpleDataSource(
                    [("Mois", "Rencontres")] +
                    [(nom_mois[item['mois']], item['nbr']) for item in par_mois]
                ),
                options = {
                    "title": "Nombre de rencontres par mois"
                }
            )

        # Graph: Fréquence de rencontres par sujet

        nbr_rencontres = rencontres.values('sujet').annotate(nbr=Count('pk')).order_by()
        context['nbr_sujets_rencontres'] = nbr_rencontres.count()


        categories = (
            ('Rencontre unique', (1,)),
            ('Entre 2 et 5 rencontres', range(2,6)),
            ('Entre 6 et 20 rencontres', range(6,20)),
            ('Plus de 20 rencontres', range(20,999)),
        )
        get_count_for_range = lambda rg: nbr_rencontres.filter(nbr__in=rg).count()
        context['graph_rencontres'] = PieWrapper(
                data= [('Type de rencontre', 'Nombre de sujets')] +
                      [(label, get_count_for_range(rg)) for label, rg in categories],
                title= 'Fréquence de rencontres'
            )
        return context



class PieChartView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/typologie.html"

    def get_graphs(self):
        sujets = self.get_sujets_queryset()
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
        queryset = self.get_fichestatistiques_queryset()
        for field in FicheStatistique._meta.fields:
            if field.__class__ in (NullBooleanField, CharField):
                yield str(field.verbose_name), PieWrapper(queryset, field)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['graphs'] = [(title, graph) for title, graph in self.get_graphs()]
        context['queryset'] = self.get_fichestatistiques_queryset()
        return context


import collections


def get_data_table(observations, continuous=False):
    return_zero = lambda: 0
    data_table = collections.defaultdict(return_zero)

    for o in observations:
        heure_debut = datetime.datetime.strptime("%s" % o.rencontre.heure_debut, "%H:%M:%S")
        if continuous:
            heure_fin = heure_debut + datetime.timedelta(0, o.rencontre.duree * 60)
        else:
            heure_fin = heure_debut

        for heure in range(heure_debut.hour, heure_fin.hour + 1):
            data_table[heure] += 1

    return data_table




class TestStatsView(FilterMixin, generic.TemplateView):
    template_name = "statistiques/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        observations = self.get_observations_queryset()

        par_heure = get_data_table(observations)
        context['par_heure'] = gchart.LineChart(
                SimpleDataSource(
                    [("Heure", "Nbr de rencontres")] +
                    [(heure, par_heure[heure]) for heure in sorted(par_heure.keys())]
                ),
                options = {
                    "title": "Nombre de rencontres par heure (démarrée)"
                }
            )

        en_continu = get_data_table(observations, continuous=True)
        context['par_heure_continu'] = gchart.LineChart(
                SimpleDataSource(
                    [("Heure", "Nbr de rencontres")] +
                    [(heure, en_continu[heure]) for heure in sorted(en_continu.keys())]
                ),
                options = {
                    "title": "Nombre de rencontres par heure (en cumulé)"
                }
            )

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
