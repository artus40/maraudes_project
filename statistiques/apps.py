from django.apps import AppConfig


class StatistiquesConfig(AppConfig):
    name = 'statistiques'

from website.decorators import Webpage

stats = Webpage('statistiques',
                icon="stats",
                defaults={
                    'title': ('Statistiques', 'app'),
                    'ajax': False,
                    'restricted': None,
                })


