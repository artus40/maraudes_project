from .notes import *
from notes.forms import *

from django.utils import timezone

class AppelForm(UserNoteForm):

    class Meta(UserNoteForm.Meta):
        model = Appel
        fields = ['sujet', 'text', 'entrant', 'created_date', 'created_time']
