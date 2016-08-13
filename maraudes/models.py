import calendar
import datetime
from django.utils import timezone

from django.db import models
from django.core.urlresolvers import reverse

from utilisateurs.models import Maraudeur, ReferentMaraude

from . import managers

## Fonctions utiles

def get_referent_maraude():
    """ Retourne l'administrateur et référent de la Maraude """
    return Maraudeur.objects.filter(is_superuser=True).first()


## Modèles


class Lieu(models.Model):
    """ Lieu de rencontre """

    nom = models.CharField(max_length=128)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Lieu de rencontre"




class Maraude(models.Model):
    """ Modèle pour une maraude
        - date : jour de la maraude
        - heure_debut :
        - heure_fin :
        - referent : maraudeur 1
        - binome : maraudeur 2

        Méthodes :
        - est_terminee : True/False
        - est_passee : True/false
    """
    objects = managers.MaraudeManager()

    date = models.DateField(
                        "Date",
                        unique=True
                    )
    # Horaires
    HORAIRES_APRESMIDI = datetime.time(16, 0)
    HORAIRES_SOIREE = datetime.time(20, 0)
    HORAIRES_CHOICES = (
        (HORAIRES_APRESMIDI, 'Après-midi'),
        (HORAIRES_SOIREE, 'Soirée')
    )
    heure_debut = models.TimeField(
                        "Horaire",
                        choices=HORAIRES_CHOICES,
                        default=HORAIRES_CHOICES[1][0]
                    )
    # Lorsque l'heure de fin est renseignée, la maraude est terminée
    heure_fin = models.TimeField(
                        "Terminée à",
                        blank=True,
                        null=True
                    )
    # Maraudeurs
    referent = models.ForeignKey(
                            "utilisateurs.Maraudeur",
                            models.CASCADE,
                            verbose_name="Référent",
                            related_name="references",
                            default=get_referent_maraude
                        )
    binome = models.ForeignKey(
                            "utilisateurs.Maraudeur",
                            models.CASCADE,
                            verbose_name="Binôme",
                            related_name="maraudes",
                            limit_choices_to={
                                'is_superuser': False,
                                'is_staff': True,
                            }
                        )

    class Meta:
        verbose_name = "Maraude"
        ordering = ['date']
        permissions = (
            ('view_maraudes', "Accès à l'application 'maraudes'"),
        )

    # TODO: A remplacer !
    JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi",
             "Vendredi", "Samedi", "Dimanche"]
    MOIS = ["Jan.", "Fév.", "Mars", "Avr.", "Mai", "Juin",
            "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]
    def __str__(self):
        return '%s %i %s' % (self.JOURS[self.date.weekday()],
                                        self.date.day,
                                        self.MOIS[self.date.month - 1])

    def est_terminee(self):
        """ Indique si la maraude est considérée comme terminée """
        if self.heure_fin is not None:
            return True
        return False
    est_terminee.admin_order_field = 'date'
    est_terminee.boolean = True
    est_terminee.short_description = 'Terminée ?'

    def est_passee(self):
        return self.date < datetime.date.today()
    est_passee.admin_order_field = 'date'
    est_passee.boolean = True
    est_passee.short_description = 'Passée ?'

    def rencontre_count(self):
        return self.rencontres.count()

    def get_observations(self):
        observations = []
        for r in self.rencontres.all():
            observations += r.observations.all()
        return observations

    def get_absolute_url(self):
        return reverse('maraudes:details', kwargs={'pk': self.id})



class Rencontre(models.Model):
    """ Une Rencontre dans le cadre d'une maraude
    """
    # Choices
    DUREE_CHOICES = (
        (5, '5 min'),
        (10, '10 min'),
        (15, '15 min'),
        (20, '20 min'),
        (30, '30 min'),
        (45, '45 min'),
        (60, '1 heure'),
    )

    # Fields
    maraude = models.ForeignKey(
                        Maraude,
                        models.CASCADE,
                        related_name = 'rencontres',
                        limit_choices_to={'heure_fin__isnull': False}
                    )
    lieu = models.ForeignKey(
                        Lieu,
                        models.CASCADE
                    )
    heure_debut = models.TimeField("Heure")
    duree = models.SmallIntegerField(
                        "Durée",
                        choices=DUREE_CHOICES
                    )

    class Meta:
        verbose_name = "Rencontre"
        ordering = ['maraude', 'heure_debut']

    def __str__(self):
        return "%s à %s (%imin)" % (
                            self.lieu,
                            self.heure_debut.strftime("%Hh%M"),
                            self.duree
                        )

    @property
    def date(self):
        return self.maraude.date

    INDIVIDU = "Individu"
    GROUPE = "Groupe"
    def groupe_ou_individu(self):
        """ Retourne le type de rencontre : 'groupe'/'individu' """
        nb = self.observations.count()
        if nb == 1:
            return self.INDIVIDU
        elif nb > 1:
            return self.GROUPE
        else:
            return "Aucun"

    def get_sujets(self):
        """ Renvoie la liste des sujets rencontrés """
        return [o.sujet for o in self.observations.all()]



class Planning(models.Model):
    """ Plannification des maraudes. Chaque instance représente un jour de la
        semaine et un horaire par défaut.
    """
    WEEKDAYS = [
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
    ]

    week_day = models.IntegerField(
                        choices=WEEKDAYS,
                        )
    horaire = models.TimeField(
                        "Horaire",
                        choices=Maraude.HORAIRES_CHOICES,
                    )

    class Meta:
        verbose_name = "Jour de maraude"
        verbose_name_plural = "Planning"

    @classmethod
    def get_planning(cls):
        """ Renvoie l'ensemble des objets enregistrés """
        return cls.objects.all()

    @classmethod
    def get_maraudes_days_for_month(cls, year, month):
        """ Renvoie le jour et l'horaire prévu de maraude, comme un tuple,
            pour l'année et le mois donnés.
        """
        planning = Planning.get_planning()
        for week in calendar.monthcalendar(year, month):
            for planned in cls.get_planning():
                day_of_maraude = week[planned.week_day]
                if day_of_maraude:
                    yield (day_of_maraude, planned.horaire)
