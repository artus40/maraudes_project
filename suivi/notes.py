from django.db import models
from notes.models import Note

class Appel(Note):

    entrant = models.BooleanField( "Appel entrant ?")

    def save(self, **kwargs):
        print('save', self)
        return super().save(**kwargs)

    def note_labels(self):      return ["Reçu" if self.entrant else "Émis", self.created_by]
    def note_bg_colors(self):   return ("warning", "info")
