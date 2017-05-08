import calendar
import datetime
from collections import OrderedDict

from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.core.urlresolvers import reverse

from utilisateurs.models import Maraudeur
from . import managers


## Fonctions utiles

def get_referent_maraude():
    """ Retourne l'administrateur et référent de la Maraude """
    return Maraudeur.objects.get_referent()

def split_by_12h_blocks(iterable):
    """ Move object with given 'field' time under 12:00 to the end of stream.
        Apart from this, order is untouched.
    """
    to_end = []
    for note in iterable:
        if getattr(note, "created_time") <= datetime.time(12):
            to_end.append(note)
        else:
            yield note

    for note in to_end:
        yield note

## Constantes

# Jours de la semaine
WEEKDAYS = [
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
        (6, "Dimanche")
    ]

# Horaires
HORAIRES_APRESMIDI = datetime.time(16, 0)
HORAIRES_SOIREE = datetime.time(20, 0)
HORAIRES_CHOICES = (
    (HORAIRES_APRESMIDI, 'Après-midi'),
    (HORAIRES_SOIREE, 'Soirée')
)

# Durées
DUREE_CHOICES = (
    (5, '5 min'),
    (10, '10 min'),
    (15, '15 min'),
    (20, '20 min'),
    (30, '30 min'),
    (45, '45 min'),
    (60, '1 heure'),
)

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
                                'is_active': True,
                            }
                        )

    class Meta:
        verbose_name = "Maraude"
        ordering = ['date']
        permissions = (
            ('view_maraudes', "Accès à l'application 'maraudes'"),
        )

    MOIS = ["Jan.", "Fév.", "Mars", "Avr.", "Mai", "Juin",
            "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]
    def __str__(self):
        return '%s %i %s' % (WEEKDAYS[self.date.weekday()][1], # Retrieve text inside tuple
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

    def get_absolute_url(self):
        return reverse('notes:details-maraude', kwargs={'pk': self.id})



class Rencontre(models.Model):
    """ Une Rencontre dans le cadre d'une maraude
    """

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

    # Should be a read only property
    def get_sujets(self):
        """ Renvoie la liste des sujets rencontrés """
        return [o.sujet for o in self.observations.all()]


class CompteRendu(Maraude):
    """ Proxy for Maraude objects.
        Gives access to related Observation and Rencontre
    """

    def observations_count(self):
        return self.rencontres.aggregate(Count("observations"))['observations__count']

    def get_observations(self, order="heure_debut", reverse=False):
        """ Returns list of all observations related to this instance """
        observations = []
        for r in self._iter(order=order, reverse=reverse):
            observations += r.observations.get_queryset()
        return list(split_by_12h_blocks(observations))

    def __iter__(self):
        """ Iterates on related 'rencontres' objects using default ordering """
        return self._iter()

    def reversed(self, order="heure_debut"):
        return self._iter(order=order, reverse=True)

    def _iter(self, order="heure_debut", reverse=False):
        """ Iterator on related 'rencontre' queryset.

            Optionnal :
            - order : order by this field, default: 'heure_debut'
            - reversed : reversed ordering, default: False
        """
        if reverse:
            order = "-" + order
        for rencontre in self.rencontres.get_queryset().order_by(order):
            yield rencontre

    class Meta:
        proxy = True



class FoyerAccueil(Lieu):
    """ Foyer d'hébergement partenaire """

    organisme = models.ForeignKey("utilisateurs.Organisme", models.CASCADE)
    jour_de_passage = models.IntegerField(
                        choices=WEEKDAYS,
                        )



class Planning(models.Model):
    """ Plannification des maraudes. Chaque instance représente un jour de la
        semaine et un horaire par défaut.
    """

    week_day = models.IntegerField(
                        primary_key=True,
                        choices=WEEKDAYS,
                        )
    horaire = models.TimeField(
                        "Horaire",
                        choices=HORAIRES_CHOICES,
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
