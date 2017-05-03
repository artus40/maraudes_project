import datetime
import random

from calendar import monthrange
from django.test import TestCase

from .models import (
    Maraude, Maraudeur, Planning,
    WEEKDAYS, HORAIRES_SOIREE,
    )
# Create your tests here.

from maraudes_project.base_data import MARAUDEURS

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

class PlanningTestCase(TestCase):

    def setUp(self):
        for i, is_maraude in enumerate(MARAUDE_DAYS):
            if is_maraude:
                Planning.objects.create(week_day=i, horaire=HORAIRES_SOIREE)

    def test_get_planning(self):
        maraudes = {i for i in range(7) if MARAUDE_DAYS[i]}
        test_maraudes = set()
        for p in Planning.get_planning():
            test_maraudes.add(p.week_day)
            self.assertEqual(p.horaire, HORAIRES_SOIREE)
        self.assertEqual(maraudes, test_maraudes)

    def test_get_maraudes_days_for_month(self):
        test_values = [
                {'year': 2017, 'month': 2,
'test': [(day, HORAIRES_SOIREE) for day in (2,3,6,7,9,10,13,14,16,17,20,21,23,24,27,28)] },
                {'year': 2016, 'month': 3,
'test': [(day, HORAIRES_SOIREE) for day in (1,3,4,7,8,10,11,14,15,17,18,21,22,24,25,28,29,31)] },
            ]

        for test in test_values:
            self.assertEqual(test['test'], list(Planning.get_maraudes_days_for_month(test['year'], test['month'])))


# TODO: Make some actual tests !!
class MaraudeManagerTestCase(TestCase):

    def setUp(self):
        for maraudeur in MARAUDEURS:
            Maraudeur.objects.create(
                **maraudeur
            )
        self.maraudeurs = Maraudeur.objects.all()
        #Set up Référent de la Maraude
        ref = self.maraudeurs[0]
        Maraudeur.objects.set_referent(ref.first_name, ref.last_name)

        l = len(self.maraudeurs)
        today = datetime.date.today()
        start_date = today.replace(month=today.month - 1 if today.month > 1 else 12,
                                   day=1)
        end_date = today.replace(month=today.month + 1 if today.month < 12 else 1,
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
