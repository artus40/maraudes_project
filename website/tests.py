from django.test import TestCase, Client

from utilisateurs.models import Maraudeur
# Create your tests here.

class RestrictedAccessAnonymousUserTestCase(TestCase):

    modules = ["maraudes", "notes", "utilisateurs"]

    def setUp(self):
        self.client = Client()

    def test_access_restricted_modules(self):
        for mod in self.modules:
            url = "/%s/" % mod
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/?next=%s" % url)


class RestrictedAccessConnectedMaraudeurTestCase(TestCase):
    modules = ["maraudes", "notes/sujets"]
    def setUp(self):
        m = Maraudeur.objects.create(first_name="Astérix", last_name="LeGaulois")
        self.client = Client()
        self.client.force_login(m)

    def test_access_restricted_modules(self):
        for mod in self.modules:
            url = "/%s/" % mod
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

class NonRestrictedAccessTestCase(TestCase):

    urls = ["/statistiques/", "/"]

    def setUp(self):
        self.client = Client()

    def test_access(self):
        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
