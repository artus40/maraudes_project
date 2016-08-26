from django.apps import AppConfig
from watson import search as watson

class SujetsConfig(AppConfig):
    name = 'sujets'

    def ready(self):
        Sujet = self.get_model("Sujet")
        watson.register(Sujet, fields=('nom', 'prenom', 'surnom'))
