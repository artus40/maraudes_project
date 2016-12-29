import datetime

from django.db import models

from django.contrib.auth.models import User, UserManager, AnonymousUser
# Create your models here.


## Visiteur

class Visiteur(AnonymousUser):

    def __str__(self):
        return "Visiteur"


class Organisme(models.Model):
    """ Organisme : Association, Entreprise, Service public, ..."""

    nom = models.CharField(max_length=64)
    email = models.EmailField("e-mail")
    adresse = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Organisme"

    def __str__(self):
        return self.nom



class Professionnel(User):
    """ Professionnel d'un organisme """
    organisme = models.ForeignKey(
                                Organisme,
                                related_name="professionnels",
                                blank=True, null=True # For now
                            )



class MaraudeurManager(UserManager):
    """ Manager for Maraudeurs objects.

    Updates `create`, `get_or_create` methods signatures : 'first_name', 'last_name'.
    Add `set_referent` method (same signature).
    """

    def create(self, first_name, last_name):
        username = "%s.%s" % (first_name[0].lower(), last_name.lower())
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': "%s@alsa68.org" % username,
            'is_staff': True,
            'is_active': True,
           }

        return super().create_user(username, **data)

    def get_or_create(self, first_name, last_name):
        try:
            maraudeur = self.get(first_name=first_name, last_name=last_name)
            created = False
        except self.model.DoesNotExist:
            created = True
            maraudeur = self.create(first_name, last_name)

        return (maraudeur, created)

    def get_referent(self):
        try:
            return self.get(is_superuser=True)
        except self.model.DoesNotExist:
            return None

    def set_referent(self, first_name, last_name):
        maraudeur, created = self.get_or_create(first_name, last_name)
        for previous in self.get_queryset().filter(is_superuser=True):
            previous.is_superuser = False
            previous.save()
        maraudeur.is_superuser = True
        maraudeur.save()
        return maraudeur



class Maraudeur(Professionnel):
    """ Professionnels qui participent aux maraudes   """

    # Donne accès aux vues "maraudes" et "suivi"

    objects = MaraudeurManager()

    class Meta:
        verbose_name = "Maraudeur"

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name[0])

