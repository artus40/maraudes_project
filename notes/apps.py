from django.apps import AppConfig
from watson import search as watson


class NotesConfig(AppConfig):
    name = 'notes'

    def ready(self):
        sujet_model = self.get_model("Sujet")
        watson.register(sujet_model, fields=('nom', 'prenom', 'surnom'))
