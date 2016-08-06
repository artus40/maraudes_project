from django.db import models

from notes.models import Note
from . import managers

# Extends 'notes' module

class Observation(Note):
    """ Note dans le cadre d'une rencontre """

    objects = managers.ObservationManager()
    rencontre = models.ForeignKey(  'maraudes.Rencontre',
                                    related_name="observations",
                                    on_delete=models.CASCADE
                                )

    class Meta:
        verbose_name = "Observation"

    def __str__(self):
        return "%s" % self.sujet


    def note_date(self):
        """ Enforce value of created_date """
        return self.rencontre.date

    def note_time(self):
        """ Enforce value of created_time """
        return self.rencontre.heure_debut

    def note_labels(self):
        return [self.rencontre.lieu, self.rencontre.heure_debut]

    def note_bg_colors(self):
        return ("info", "info")



