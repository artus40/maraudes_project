import datetime

from django.db.models.functions.datetime import ExtractMonth
from django.db.models import (Field, NullBooleanField,
                              Count,
                              )
from graphos.sources.simple import SimpleDataSource
from graphos.renderers import gchart

from notes.models import Sujet

NOM_MOIS = {
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
# Defines generic labels for common fields
LABELS = {
        NullBooleanField: {True: "Oui", False: "Non", None: "Ne sait pas"},
    }

# TODO: Retrieve charts data from cache to avoid recalculating on each request
class CachedDataSource:
    pass

# TODO: Clean up...


class FieldValuesCountDataSource(SimpleDataSource):
    """ Generates data from a limited set of choices.

    """
    def __init__(self, queryset, field, labels=None, excluded=None):
        self.queryset = queryset
        self.field_name = field.name
        self.excluded = excluded or []
        if not labels:
            if field.__class__ in LABELS:
                labels = LABELS[field.__class__]
            elif field.choices:
                labels = dict(field.choices)
            else:
                raise ValueError("Could not retrieve labels for", field)
        self.labels = labels
        super().__init__(self.create_data())

    def create_data(self):
        data = [(self.field_name, "%s_count" % self.field_name)]  # Headers
        data += [
            (self.labels[item[self.field_name]],  # Display a label instead of raw values
             item['count']
             ) for item in self.queryset.values(            # Retrieve all values for field
                                            self.field_name
                                        ).annotate(         # Count occurrences of each value
                                            count=Count('pk')
                                        ).order_by()        # Needed so that counts are aggregated
            # Exclude values that are marked to be ignored
            if (not self.excluded
                or item[self.field_name] not in self.excluded)
        ]
        return data


class PieWrapper(gchart.PieChart):
    """ A wrapper around gchart.PieChart that generates a graph from :

        - a queryset and a model field (NullBooleanField or field with choices)
        OR
        - a data object and title
    """

    options = {
        'is3D': False,
        'pieSliceText': 'value',
        'legend': {'position': 'labeled', 'maxLines': 3, 'textStyle': {'fontSize': 16, }},
    }
    height = 400
    width = 800

    def __init__(self,
                 queryset=None, field=None,
                 data=None, title=None,
                 null_values=None,
                 **kwargs):
        if data is None:
            if not isinstance(field, Field):
                raise TypeError(field, 'must be a child of django.models.db.fields.Field !')
            data_source = FieldValuesCountDataSource(
                queryset, field,
                excluded=null_values,
                labels=None  # TODO: How to pass in labels ??
            )
        else:
            data_source = SimpleDataSource(data=data)

        options = self.options.copy()
        options.update(
            title=getattr(field, 'verbose_name', title)
        )
        super().__init__(data_source,
                         options=options,
                         width=kwargs.get('width', self.width),
                         height=kwargs.get('height', self.height),
                         )

    def get_js_template(self):
        return "statistiques/gchart/pie_chart.html"

    def get_html_template(self):
        return "statistiques/gchart/html.html"


class ColumnWrapper(gchart.ColumnChart):

    options = {
        'is3D': False,
        'legend': {'position': 'labeled', 'maxLines': 3, 'textStyle': {'fontSize': 16, }},
        'title': 'test',
    }

    def __init__(self, *args, **kwargs):
        kwargs.update(options=self.options.copy())
        super().__init__(*args, **kwargs)


class DonneeGeneraleChart(gchart.BarChart):

    def __init__(self, maraudes=None, rencontres=None, sujets=None):

        data = [("...", "Soirée", "Journée", { 'role': 'annotation'})]

        data += [("Maraudes", maraudes[2].count(), maraudes[1].count(), maraudes[0].count())]
        data += [("Rencontres", rencontres[2].count(), rencontres[1].count(), rencontres[0].count())]
        if sujets:
            data += [("Nouvelles rencontres", sujets[2].count(), sujets[1].count(), sujets[0].count())]

        super().__init__(SimpleDataSource(data), options={'title': 'Données générales', 'isStacked': 'percent'})

def generate_piechart_for_field(field):
    """ Returns a PieWrapper subclass working with a fixed field """
    class FieldChart(PieWrapper):
        def __init__(self, queryset):
            super().__init__(queryset, field)
    return FieldChart


class GenrePieChart(PieWrapper):
    def __init__(self, queryset):
        queryset = Sujet.objects.filter(pk__in=queryset.values_list('pk'))
        super().__init__(queryset, Sujet._meta.get_field('genre'))


class AgePieChart(PieWrapper):
    """ Chart for 'age' field of Sujet model """

    labels = (('Mineurs', range(0, 18)),
              ('18-24', range(18, 25)),
              ('25-34', range(25, 35)),
              ('35-44', range(35, 45)),
              ('45-54', range(45, 55)),
              ('+ de 55', range(55, 110)),
              )

    def count_nbr_sujets(self, age_rng):
        return self.queryset.filter(age__in=age_rng).count()

    def __init__(self, queryset):
        data = [("age", "count")]
        if queryset:
            self.queryset = Sujet.objects.filter(pk__in=queryset.values_list('pk'))
            data += [(label, self.count_nbr_sujets(rg)) for label, rg in self.labels]
            data += [("Ne sait pas", self.queryset.filter(age=None).count())]
        super().__init__(data=data, title="Âge")


class RencontreParSujetChart(PieWrapper):

    labels = (('Rencontre unique', (1,)),
              ('Entre 2 et 5 rencontres', range(2, 6)),
              ('Entre 6 et 20 rencontres', range(6, 20)),
              ('Plus de 20 rencontres', range(20, 999)),
              )

    def get_count_for_range(self, rng):
        return self.queryset.filter(nbr__in=rng).count()

    def __init__(self, queryset):
        data = [('Type de rencontre', 'Nombre de sujets')]
        if queryset:
            self.queryset = queryset.values('sujet').annotate(nbr=Count('pk')).order_by()
            data += [(label, self.get_count_for_range(rg)) for label, rg in self.labels]
        super().__init__(data=data,
                         title='Fréquence de rencontres'
                         )


class RencontreParMoisChart(gchart.ColumnChart):

    def __init__(self, queryset):
        data = [("Mois", "Rencontres")]
        if queryset:
            par_mois = queryset.annotate(
                                mois=ExtractMonth('created_date')
                            ).values(
                                'mois'
                            ).annotate(
                                nbr=Count('pk')
                            ).order_by()
            data += [(NOM_MOIS[item['mois']], item['nbr']) for item in par_mois]
        else:
            data += [("Mois",0)]
        super().__init__(SimpleDataSource(data),
                         options={
                            "title": "Nombre de rencontres par mois"
                            }
                         )


class RencontreParHeureChart(gchart.AreaChart):
    def __init__(self, queryset):
        data = [("Heure", "Rencontres démarrées", "Au total (démarré + en cours)")]
        if queryset:
            par_heure = self.calculer_frequentation_par_quart_heure(queryset, continu=False)
            en_continu = self.calculer_frequentation_par_quart_heure(queryset, continu=True)
            data += [(heure, par_heure[heure], en_continu[heure]) for heure in sorted(par_heure.keys())]
        else:
            data += [("Heure", 0, 0)]
        super().__init__(SimpleDataSource(data),
                         options={
                            "title": "Fréquentation de la maraude en fonction de l'heure (par quart d'heure)"
                            }
                         )

    @staticmethod
    def calculer_frequentation_par_quart_heure(observations, continu=False):
        """ Calcule le nombre d'observations, de 16h à 24h, par tranche de 15min.
            L'algorithme est *très peu* efficace mais simple à comprendre : on calcule pour
            chaque tranche les observations qui y sont contenues.
            On peut calculer seulement les observations démarrées (continu = False) ou considérer
            que l'observation est contenue dans un intervalle sur toute sa durée (continu = True).

        """
        data = dict()

        def genere_filtre_pour(heure, indice):
            """ Renvoie une fonction qui renvoie True si l'intervalle donné contient l'observation, c'est-à-dire :
            1. Elle démarre/finit dans l'intervalle.
            2. Elle démarre avant et fini après l'intervalle.
            """
            debut_intervalle = indice * 15
            fin_intervalle = debut_intervalle + 15
            rng = range(debut_intervalle, fin_intervalle)

            def est_contenue(observation):
                """ Vérifie l'observation est contenue dans l'intervalle """
                debut = datetime.datetime.strptime(
                    "%s" % observation.rencontre.heure_debut,
                    "%H:%M:%S"
                )
                fin = debut + datetime.timedelta(0, observation.rencontre.duree * 60)

                # L'observation démarre dans l'intervalle
                if debut.hour == heure and debut.minute in rng:
                    return True
                # L'observation finit dans l'intervalle, seulement si continu est True
                elif continu and (fin.hour == heure and fin.minute in rng):
                    return True
                # L'observation démarre avant ET finit après l'intervalle,
                # seulement si continu est True
                elif (continu
                      and (debut.hour <= heure and debut.minute <= debut_intervalle)
                      and (fin.hour >= heure and fin.minute >= fin_intervalle)):
                    return True
                else:
                    return False

            return est_contenue

        for h in range(16, 24):
            for i in range(4):
                filtre = genere_filtre_pour(heure=h, indice=i)
                contenus = list(filter(filtre, observations))

                key = datetime.time(h, i * 15)
                data[key] = len(contenus)

        return data
