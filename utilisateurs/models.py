import datetime

from django.db import models
from django.contrib.auth.models import User, UserManager, AnonymousUser
# Create your models here.



class Organisme(models.Model):
    """ Organisme : Association, Entreprise, Service public, ..."""

    nom = models.CharField(max_length=64, primary_key=True)
    email = models.EmailField("e-mail", blank=True, null=True)
    adresse = models.CharField(max_length=128, blank=True, null=True)

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
    """

    def get_referent(self):
        try:
            return self.get(is_superuser=True)
        except self.model.DoesNotExist:
            return None

    def set_referent(self, first_name, last_name):
        maraudeur, created = self.get_or_create(first_name=first_name, last_name=last_name)
        for previous in self.get_queryset().filter(is_superuser=True):
            previous.is_superuser = False
            previous.save()
        maraudeur.is_superuser = True
        maraudeur.save()
        return maraudeur



class Maraudeur(Professionnel):
    """ Professionnel qui participe aux maraudes """

    def est_referent(self):
        return self.is_superuser
    est_referent.boolean = True
    est_referent.short_description = 'Référent Maraude'

    objects = MaraudeurManager()

    class Meta:
        verbose_name = "Maraudeur"

    def save(self, *args, **kwargs):
        self.username = "%s.%s" % (self.first_name[0].lower(), self.last_name.lower())
        self.email = "%s@alsa68.org" % self.username
        self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

