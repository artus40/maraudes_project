import datetime

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from .managers import MaraudeurManager
# Create your models here.

if not settings.MARAUDEURS:
    raise ImproperlyConfigured("No configuration for Maraudeur model")
else:
    try:
        assert(isinstance(settings.MARAUDEURS.get('organisme'), dict))
    except:
        raise ImproperlyConfigured("'organisme' key of MARAUDEURS settings is not a dict !")


def get_email_suffix(organisme):
    if not organisme.email:
        return "unconfigured.org"
    else:
        return organisme.email.split("@")[1]



class Organisme(models.Model):
    """ Organisme : Association, Entreprise, Service public, ..."""

    nom = models.CharField(max_length=64, primary_key=True)
    email = models.EmailField("e-mail")
    adresse = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = "Organisme"

    def __str__(self):
        return self.nom



class Professionnel(User):
    """ Professionnel d'un organisme """
    organisme = models.ForeignKey(Organisme,
                                models.CASCADE,
                                related_name="professionnels",
                            )

    def make_username(self):
        """ Build the username for this Professionel instance. Must be overriden."""
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self.username = self.make_username()
        if not self.pk:
            self.email = "%s@%s" % (self.username, get_email_suffix(self.organisme))
        return super().save(*args, **kwargs)



class Maraudeur(Professionnel):
    """ Professionnel qui participe aux maraudes """

    @staticmethod
    def get_organisme():
        return Organisme.objects.get_or_create(**settings.MARAUDEURS['organisme'])[0]

    def est_referent(self):
        return self.is_superuser
    est_referent.boolean = True
    est_referent.short_description = 'Référent Maraude'

    objects = MaraudeurManager()

    class Meta:
        verbose_name = "Maraudeur"

    def make_username(self):
        return "%s.%s" % (self.first_name[0].lower(), self.last_name.lower())

    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_staff = True
            self.organisme = Maraudeur.get_organisme()
            self.set_password(settings.MARAUDEURS['password'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return "%s %s." % (self.first_name, self.last_name[0])

