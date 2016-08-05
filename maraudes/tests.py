import datetime
import random

from calendar import monthrange
from django.test import TestCase

from .models import Maraude, Maraudeur, ReferentMaraude
# Create your tests here.

from alsa.base_data import MARAUDEURS

MARAUDE_DAYS = [
    True, True, False, True, True, False, False
]

def get_maraude_days(start, end):
    """ Iterator that returns date of maraude within start-end range """
    maraude_days = []
    first_loop = True
    for m in range(start.month, end.month + 1):
        start_day = 1
        if first_loop:
            start_day = start.day
            first_loop = False

        month_range = monthrange(start.year, m)[1]
        for d in range(start_day, month_range + 1):
            date = datetime.date(start.year, m, d)
            if MARAUDE_DAYS[date.weekday()]:
                maraude_days.append(date)

    return maraude_days

class MaraudeManagerTestCase(TestCase):

    def setUp(self):
        for maraudeur in MARAUDEURS:
            Maraudeur.objects.create(
                **maraudeur
            )
        self.maraudeurs = Maraudeur.objects.all()
        #Set up Référent de la Maraude
        ref = self.maraudeurs[0]
        ReferentMaraude.objects.create(
            maraudeur=ref
        )

        l = len(self.maraudeurs)
        today = datetime.date.today()
        start_date = today.replace(month=today.month - 1,
                                   day=1)
        end_date = today.replace(month=today.month + 1,
                                 day=28)
        for i, date in enumerate(get_maraude_days(start_date, end_date)):
            i = i % l
            if i == 0:
                replacement = random.randint(1, l-1)
                binome = random.randint(1, l-1)
                while binome == replacement:
                    binome = random.randint(1, l-1)

                Maraude.objects.create(
                    date=date,
                    referent=self.maraudeurs[replacement],
                    binome=self.maraudeurs[binome], # Avoid 0 = referent
                )
            else:
                Maraude.objects.create(
                    date=date,
                    referent=ref,
                    binome=self.maraudeurs[i]
                )

    def test_future_maraudes(self):
        """ La liste des futures maraudes """
        pass

    def test_past_maraudes(self):
        pass

    def test_get_next_maraude(self):
        pass

    def test_get_next_of(self):
        pass

    def test_all_of_with_referent(self):
        pass

    def test_all_of_with_maraudeur(self):
        pass


class MaraudeTestCase(TestCase):

    def test_est_terminee(self):
        pass


class RencontreTestCase(TestCase):
    pass
