import datetime

from calendar import monthrange
from django.test import TestCase

from .models import (
    Maraude, Maraudeur, Planning,
    HORAIRES_SOIREE,
    )


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
             'test': [(day, HORAIRES_SOIREE) for day in (2, 3, 6, 7, 9, 10, 13, 14, 16,
                                                         17, 20, 21, 23, 24, 27, 28)]},
            {'year': 2016, 'month': 3,
             'test': [(day, HORAIRES_SOIREE) for day in (1, 3, 4, 7, 8, 10, 11, 14, 15,
                                                         17, 18, 21, 22, 24, 25, 28, 29, 31)]},
        ]

        for test in test_values:
            self.assertEqual(test['test'], list(Planning.get_maraudes_days_for_month(test['year'], test['month'])))


class MaraudeManagerTestCase(TestCase):

    maraudeurs = [
        {"first_name": "Astérix", "last_name": "Le Gaulois"},
        {"first_name": "Obélix", "last_name": "et Idéfix"}]

    def setUp(self):
        first = True
        for maraudeur in self.maraudeurs:
            if first:
                first = False
                self.referent = Maraudeur.objects.set_referent(*list(maraudeur.values()))
            else:
                self.binome = Maraudeur.objects.create(
                    **maraudeur
                )

        self.today = datetime.date.today()
        self.past_dates = [self.today - datetime.timedelta(d) for d in (1, 3, 5)]
        self.future_dates = [self.today + datetime.timedelta(d) for d in (2, 4, 6)]

        for date in [self.today, ] + self.past_dates + self.future_dates:
            Maraude.objects.create(
                date=date,
                referent=self.referent,
                binome=self.binome
            )

    @staticmethod
    def retrieve_date(maraude):
        return maraude.date

    def test_all_of(self):
        _all = set([self.today, ] + self.past_dates + self.future_dates)
        for maraudeur in self.maraudeurs:
            maraudeur = Maraudeur.objects.get(**maraudeur)
            self.assertEqual(
                set(map(self.retrieve_date, Maraude.objects.all_of(maraudeur))),
                _all
                )

    def test_future_maraudes_no_args(self):
        """ La liste des futures maraudes """
        test_set = set(self.future_dates + [self.today, ])
        check_set = set(map(self.retrieve_date, Maraude.objects.get_future()))
        self.assertEqual(test_set, check_set)

    def test_future_maraudes_are_sorted_by_date(self):
        check_generator = iter(sorted(self.future_dates + [self.today, ]))
        for maraude in Maraude.objects.get_future():
            self.assertEqual(maraude.date, next(check_generator))

    def test_past_maraudes_are_sorted_by_date(self):
        check_generator = iter(sorted(self.past_dates))
        for maraude in Maraude.objects.get_past():
            self.assertEqual(maraude.date, next(check_generator))

    def test_past_maraudes_no_args(self):
        check_set = set(self.past_dates)
        test_set = set(map(self.retrieve_date, Maraude.objects.get_past()))
        self.assertEqual(test_set, check_set)

    def test_next_property(self):
        self.assertEqual(self.retrieve_date(Maraude.objects.next), self.today)

    def test_last_property(self):
        self.assertEqual(self.retrieve_date(Maraude.objects.last), max(self.past_dates))

    def test_get_next_of(self):
        self.assertEqual(self.retrieve_date(Maraude.objects.get_next_of(self.binome)), self.today)


class MaraudeTestCase(TestCase):

    def test_est_terminee(self):
        pass


class RencontreTestCase(TestCase):
    pass
