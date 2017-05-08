from django.apps import AppConfig
from watson import search as watson

class NotesConfig(AppConfig):
    name = 'notes'

    def ready(self):
        Sujet = self.get_model("Sujet")
        watson.register(Sujet, fields=('nom', 'prenom', 'surnom'))
