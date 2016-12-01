import datetime

from django.db import models

from django.contrib.auth.models import User, AnonymousUser
# Create your models here.

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

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



class Maraudeur(Professionnel):
    """ Professionnels qui participent aux maraudes   """

    auto_fields = ['username', 'email', 'organisme']

    # Donne accès aux vues "maraudes" et "suivi"

    DEFAULT_ORGANISME = "ALSA"

    class Meta:
        verbose_name = "Maraudeur"

    def _fill_fields(self):
        for field in self.auto_fields:
            filling_func = "fill_%s" % field
            try:
                val = getattr(self, filling_func)()
            except AttributeError:
                raise ValueError("'%s' is not defined on %s" % (filling_func, self))
            setattr(self, field, val)

    def fill_email(self):
        return "%s@alsa68.org" % self.username

    def fill_username(self):
        return "%s.%s" % (self.first_name[0].lower(), self.last_name.lower())

    def fill_organisme(self):
        try:
            return Organisme.objects.get(nom=self.DEFAULT_ORGANISME)
        except Organisme.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk or not self.username or not self.email:
            self._fill_fields()
            self.is_staff = True

        return super(Maraudeur, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name[0])



class ReferentMaraude(SingletonModel):
    """ Référent de la maraude """
    maraudeur = models.ForeignKey(Maraudeur)

    class Meta:
        verbose_name = "Référent de la maraude"

    def __str__(self):
        return 'Referent: %s' % self.maraudeur

    def set_unique_referent(self):
        """ Ensure 'is_referent' has only one 'True' value """
        for maraudeur in Maraudeur.objects.all():
            if maraudeur == self.maraudeur:
                maraudeur.is_superuser= True
                maraudeur.save()
            else:
                if maraudeur.is_superuser:
                    maraudeur.is_superuser = False
                    maraudeur.save()

    def save(self, *args, **kwargs):
        # On s'assure que le référent (administrateur) est unique
        self.set_unique_referent()
        return super().save(*args, **kwargs)

    @classmethod
    def get_referent(cls):
        instance = cls.load()
        return instance.maraudeur
