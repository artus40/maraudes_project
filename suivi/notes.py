from django.db import models
from notes.models import Note

class Appel(Note):

    entrant = models.BooleanField( "Appel entrant ?")

    def note_labels(self):      return ["Reçu" if self.entrant else "Émis", self.created_by]
    def note_bg_colors(self):   return ("warning", "info")


class Signalement(Note):

    source = models.ForeignKey("utilisateurs.Organisme")

    def note_labels(self): return [self.source, self.created_by]
    def note_bg_colors(self): return ('warning', 'info')



