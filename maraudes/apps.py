from django.apps import AppConfig


class Config(AppConfig):
    name = 'maraudes'

    index_url = "/maraudes/"
    menu_icon = "road"
    def get_index_url(self):
        return "/maraudes/"


from utilisateurs.models import Maraudeur
from website.decorators import Webpage

maraudes = Webpage('maraudes',
                icon="road",
                defaults={
                'users': [Maraudeur],
                'ajax': False,
                'title': ('Maraudes','app'),
            })
# Setting up some links
maraudes.app_menu.add_link(('Liste des maraudes', 'maraudes:liste', "list"))
maraudes.app_menu.add_link(('Planning', 'maraudes:planning', "calendar"), admin=True)

#Dropdowns ??
# Liste des maraudes
## Filtres...

# Détails de compte-rendu
## Précédent, suivant

# Création/Edition de compte-rendu
## Menu création : nouveau sujet, nouveau lieu -> modal ou pop-over ??
