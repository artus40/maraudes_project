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

#Hack to create class-wide links
#Needs some thinking...

from website.navbar import Link
maraudes.app_menu._links.append(Link('Liste des maraudes', 'maraudes:liste', "list"))
