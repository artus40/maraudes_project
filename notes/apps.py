from django.apps import AppConfig
from watson import search as watson

from utilisateurs.models import Maraudeur
from website.decorators import Webpage
notes = Webpage("notes", icon="pencil", defaults={
                        'restricted': [Maraudeur],
                        'ajax': False,
                    }
                )

class NotesConfig(AppConfig):
    name = 'notes'

    def ready(self):
        Sujet = self.get_model("Sujet")
        watson.register(Sujet, fields=('nom', 'prenom', 'surnom'))
