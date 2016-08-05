from django.contrib import admin

from .models import Sujet


@admin.register(Sujet)
class SujetAdmin(admin.ModelAdmin):

    fieldsets = [
            ('Identité', {'fields': [('nom', 'prenom'), 'genre']}),
            ('Informations', {'fields': ['age', ]}),
        ]


