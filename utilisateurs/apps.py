from django.apps import AppConfig

from website.decorators import Webpage
from .models import Professionnel

class UtilisateursConfig(AppConfig):
    name = 'utilisateurs'


utilisateurs = Webpage('utilisateurs',
                icon="user",
                defaults={
                'users': [Professionnel],
                'ajax': False,
                'title': ('Utilisateurs','app'),
            })
