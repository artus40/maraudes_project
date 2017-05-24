from django.test import TestCase

from utilisateurs.models import Maraudeur, Professionnel
# Create your tests here.
def generate_names():
    i = 0
    while True:
        yield {'first_name': 'name%i' % i, 'last_name': 'family%i' % i}
        i += 1

class ProfessionelTestCase(TestCase):
    pass


class MaraudeurTestCase(TestCase):

    maraudeurs = generate_names()

    def create(self):
        return Maraudeur.objects.create(**next(self.maraudeurs))

    def test_email_set_on_creation(self):
        m = self.create()
        self.assertIsNotNone(m.email)

    def test_username_set_on_creation(self):
        m = self.create()
        self.assertEqual(m.username, Maraudeur.make_username(m))

    def test_maraudeurs_is_staff(self):
        m = self.create()
        self.assertEqual(m.is_staff, True)

    def test_username_set_on_update(self):
        m = self.create()
        m.last_name = "test01"
        m.save()
        self.assertEqual(m.username, "%s.test01" % (m.first_name[0]))

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
