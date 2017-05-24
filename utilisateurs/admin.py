from django.contrib import admin, messages

from .models import *
# Register your models here.

admin.register(Organisme)


@admin.register(Maraudeur)
class MaraudeurAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identité', {'fields': [('first_name', 'last_name'),]}),
        ('Contact', {'fields': [('organisme','email',)]}),
        ('Statut', {'fields': [('is_active',)]}),
    ]

    list_display = ('username', 'is_active', 'est_referent')
    actions = ['set_referent', 'toggle_staff']
    ordering = ['-is_active', 'username']

    def get_changeform_initial_data(self, request):
        return {'organisme': Maraudeur.get_organisme(),
                'is_active': True,
                }

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

    def toggle_staff(self, request, queryset):
        try:
            for m in queryset:
                m.is_active = not m.is_active
                m.save()
            self.message_user(request,
                              "%i maraudeurs ont été modifié(s)" % len(queryset),
                              level=messages.SUCCESS)
        except:
            self.message_user(request, "Erreur lors de l'inversion", level=messages.WARNING)
    toggle_staff.short_description = "Inverser le statut actif"

@admin.register(Organisme)
class OrganismeAdmin(admin.ModelAdmin):
    pass


