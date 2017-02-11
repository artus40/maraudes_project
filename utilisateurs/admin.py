from django.contrib import admin

from .models import *
# Register your models here.

admin.register(Organisme)


@admin.register(Maraudeur)
class MaraudeurAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Informations', {'fields': [('first_name', 'last_name')]}),
    ]

    list_display = ('username', 'is_active')



@admin.register(Organisme)
class OrganismeAdmin(admin.ModelAdmin):
    pass
