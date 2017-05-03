from django.contrib import admin, messages

from .models import *
# Register your models here.

admin.register(Organisme)


@admin.register(Maraudeur)
class MaraudeurAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Informations', {'fields': [('first_name', 'last_name'),('email',)]}),
        ('Organisme', {'fields': [('organisme',)]}),
        ('Statut', {'fields': [('is_active',)]}),
    ]

    list_display = ('username', 'is_active', 'est_referent')
    actions = ['set_referent']

    def set_referent(self, request, queryset):
        if len(queryset) > 1:
            self.message_user(
                    request,
                    "Vous ne pouvez définir qu'un seul référent !",
                    level=messages.WARNING)
            return
        maraudeur = queryset.first()
        Maraudeur.objects.set_referent(maraudeur.first_name, maraudeur.last_name)
        self.message_user(request, "%s a été défini comme référent." % maraudeur,
                          level=messages.SUCCESS)
    set_referent.short_description = "Définir comme référent"


@admin.register(Organisme)
class OrganismeAdmin(admin.ModelAdmin):
    pass
