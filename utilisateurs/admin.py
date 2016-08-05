from django.contrib import admin

from .models import *
# Register your models here.

admin.register(Organisme)


@admin.register(Maraudeur)
class MaraudeurAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Informations', {'fields': [('first_name', 'last_name')]}),
    ]

    list_display = ('first_name', 'last_name', 'is_superuser')


@admin.register(ReferentMaraude)
class ReferentMaraudeAdmin(admin.ModelAdmin):
    fields = ['maraudeur']
