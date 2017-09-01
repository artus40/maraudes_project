from django.contrib import admin

from .models import *
from statistiques.models import FicheStatistique
# Register your models here.


class FicheStatistiqueInline(admin.StackedInline):
    model = FicheStatistique
    can_delete = False


@admin.register(Sujet)
class SujetAdmin(admin.ModelAdmin):

    fieldsets = [
            ('Identité', {'fields': [('nom', 'surnom', 'prenom', ), ('genre', 'age')]}),
        ]

    inlines = [
        FicheStatistiqueInline,
    ]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Contexte', {
                        'fields': ['created_by', ('created_date', 'created_time')]
                        }),
        ('Note', {
                        'fields': ['sujet', 'text']}),
    ]

    list_display = ['created_date', 'sujet', 'type_name', 'text']
    list_filter = ('created_date', 'created_by')
