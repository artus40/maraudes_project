from django.apps import AppConfig


class SuiviConfig(AppConfig):
    name = 'suivi'

from utilisateurs.models import Maraudeur
from website.decorators import Webpage
suivi = Webpage("suivi", icon="eye-open", defaults={
                        'restricted': [Maraudeur],
                        'ajax': False,
                    }
                )

suivi.app_menu.add_link(('Liste des sujets', 'suivi:liste', 'list'))

