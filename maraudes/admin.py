from django.contrib import admin

from .models import Lieu, Rencontre, Maraude, Planning
from .notes import Observation

# Basic registration
admin.site.register(Lieu)


# Inlines
class ObservationInline(admin.StackedInline):
    model = Observation
    extra = 0
    exclude = ('created_date', 'created_time', 'created_by')


@admin.register(Rencontre)
class RencontreAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Contexte', {'fields': ['maraude', 'lieu', ('heure_debut', 'duree')]})
    ]

    inlines = [ObservationInline]

    list_display = ('maraude', 'lieu', 'heure_debut', 'groupe_ou_individu')
    list_filter = ['lieu']


@admin.register(Maraude)
class MaraudeAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Plannification', {
            'fields': [('date', 'heure_debut'),
                       ('referent', 'binome')]
            }),
        ('Gestion', {
            'fields': ['heure_fin'],
            }),
    ]
    list_display = ('date', 'heure_debut', 'binome', 'est_passee', 'est_terminee')
    list_filter = ['date', 'binome']
    ordering = ['-date']


@admin.register(Planning)
class PlanningAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [('week_day', 'horaire')]})]
    list_display = ('week_day', 'horaire')
