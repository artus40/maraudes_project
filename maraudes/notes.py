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
        return "<Observation: %s>" % self.sujet

    def get_date(self):
        return self.rencontre.date

    def get_header(self):
        return ('Rencontre', [self.rencontre.lieu, "%smin" % self.rencontre.duree])
