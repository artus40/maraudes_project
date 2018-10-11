from django.db import models
from notes.models import Note


# Extends 'notes' module


class Observation(Note):
    """ Note dans le cadre d'une rencontre """

    rencontre = models.ForeignKey('maraudes.Rencontre',
                                  models.CASCADE,
                                  related_name="observations")

    # Note attributes proxies
    def note_author(self): return self.rencontre.maraude.referent

    def note_date(self): return self.rencontre.date

    def note_time(self): return self.rencontre.heure_debut

    def note_labels(self): return [self.rencontre.lieu, self.rencontre.heure_debut]

    def note_bg_colors(self): return "info", "info"


class Appel(Note):

    entrant = models.BooleanField("Appel entrant ?")

    def note_labels(self):
        return ["Reçu" if self.entrant else "Émis", self.created_by]

    def note_bg_colors(self):
        return "warning", "info"


class Signalement(Note):

    source = models.ForeignKey("utilisateurs.Organisme", on_delete=models.CASCADE)

    def note_labels(self):
        return [self.source, self.created_by]

    def note_bg_colors(self):
        return 'danger', 'info'
