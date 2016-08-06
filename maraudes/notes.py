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

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = self.rencontre.date
        return super().save(*args, **kwargs)
