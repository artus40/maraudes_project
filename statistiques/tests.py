from django.test import TestCase
from datetime import date, time

from maraudes.models import Maraude, Rencontre, Lieu
from notes.models import Sujet
from utilisateurs.models import Maraudeur
from maraudes.notes import Observation
from .charts import RencontreParHeureChart

# Create your tests here.

# MANDATORY FEATURES

# FicheStatistique primary key IS it's foreign sujet pk
class TestCalculerFrequentationParHeure(TestCase):

    def setUp(self):
        maraude = Maraude.objects.create(date=date(2017, 1, 1),
                                         heure_debut=time(20, 00),
                                         binome=Maraudeur.objects.create(first_name="Asterix", last_name="Gaulois"),
                                         referent=Maraudeur.objects.create(first_name="Referent", last_name="R", is_superuser=True))
        self._generate_test_data(maraude, [
            ("Gare", time(20, 30), 45, ("S1",)),  #
            ("Gare", time(20, 40), 10, ("S2", "S3",)),
            ("Centre-ville", time(21, 30), 30, ("S4",)), # Borne finale fermée
            ("Urgences", time(22, 20), 26, ("S5", "S3")),  # Déborde sur un nouvel intervalle
        ])

    def _generate_test_data(self, maraude, data):
        for lieu, heure, duree, sujets in data:
            rencontre = Rencontre.objects.create(maraude=maraude,
                                                 lieu=Lieu.objects.get_or_create(nom=lieu)[0],
                                                 heure_debut=heure,
                                                 duree=duree)
            for s in sujets:
                observation = Observation.objects.create(rencontre=rencontre,
                                                         sujet=Sujet.objects.get_or_create(surnom=s)[0],
                                                         text="RAS")

    def differences(self, first, second):
        diff = dict()
        for key, val in first.items():
            try:
                if not second[key] == val:
                    diff[key] = (val, second[key])
            except KeyError:
                diff[key] = (val, None)
        return diff

    def test_with_test_data(self):

        # Retrieve observations queryset
        queryset = Observation.objects.filter(created_date=date(2017,1,1))

        non_continu = RencontreParHeureChart.calculer_frequentation(queryset, continu=False)
        continu = RencontreParHeureChart.calculer_frequentation(queryset, continu=True)
        test_non_continu = {time(20, 30): 3,
                            time(21, 30): 1,
                            time(22, 15): 2,
                            }
        self.assertEqual(non_continu, test_non_continu, "\nDifferences :\n{}".format(self.differences(non_continu, test_non_continu)))

        test_continu = {time(20, 30): 3, time(20, 45): 3,
                        time(21, 0): 1, time(21, 30): 1, time(21, 45): 1,
                        time(22, 15): 2, time(22, 30): 2, time(22, 45): 2,
                        }
        self.assertEqual(continu, test_continu,  "\nDifferences :\n{}".format(self.differences(continu, test_continu)))