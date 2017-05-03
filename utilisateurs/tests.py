from django.test import TestCase

from .models import Maraudeur, Professionnel
# Create your tests here.


class MaraudeurManagerTestCase(TestCase):

    names = [
        {'first_name': 'Astérix', 'last_name': 'Devinci'},
        {'first_name': 'Obélix', 'last_name': 'Idéfix'},
    ]


    def setUp(self):
        for name in self.names:
            Maraudeur.objects.create(**name)

    def test_get_or_create_from_first_and_last_name(self):
        # Existing Maraudeur
        get_maraudeur = Maraudeur.objects.get(first_name="Obélix", last_name="Idéfix")
        maraudeur, created = Maraudeur.objects.get_or_create(first_name='Obélix', last_name='Idéfix')
        self.assertEqual(created, False)
        self.assertEqual(maraudeur, get_maraudeur)
        # Non-existing Maraudeur
        with self.assertRaises(Maraudeur.DoesNotExist):
            Maraudeur.objects.get(first_name="Thierry", last_name="Lhermitte")
        maraudeur, created = Maraudeur.objects.get_or_create(first_name='Thierry', last_name='Lhermitte')
        self.assertEqual(created, True)
        self.assertEqual(maraudeur, Maraudeur.objects.get(username="t.lhermitte"))

    def test_set_referent_maraude(self):
        # Set a first referent, non-existing Maraudeur
        referent1 = Maraudeur.objects.set_referent("Claudine", "Henry")
        self.assertEqual(referent1.is_superuser, True)
        self.assertEqual(referent1, Maraudeur.objects.get_referent())
        # Set a new referent, existing Maraudeur
        referent2 = Maraudeur.objects.set_referent("Astérix", "Devinci")
        self.assertEqual(referent2.is_superuser, True)
        self.assertEqual(referent2, Maraudeur.objects.get_referent())
        self.test_referent_is_unique()

    def test_referent_is_unique(self):
        superusers = []
        for m in Maraudeur.objects.all():
            if m.is_superuser:
                superusers.append(m)
        self.assertLess(len(superusers), 2)
