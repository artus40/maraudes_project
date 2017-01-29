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

# Admin dropdown
"""
class SujetsDropdown:
    header = "Gérer les sujets"

    links = [
        ('Nouveau sujet', 'sujets:create', 'plus'),
        ('Administration', ('admin:app_list', {'app_label': 'sujets' }), 'wrench'),
    ]

"""
# Suivi:Details
# new link: ('Éditer les notes', ('admin:notes_note_changelist', {'get': {'sujet__personne_ptr': sujet.pk}}), 'wrench') 
