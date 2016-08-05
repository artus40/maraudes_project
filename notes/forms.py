from .models import Note
from django import forms

from django_select2.forms import Select2Widget
from django.forms import Textarea

class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ['sujet', 'text']
        widgets = {
            'sujet': Select2Widget(),
            'text': Textarea(attrs={'rows':4}),
        }

    def save(self, *args, **kwargs):
        # Get data for extra fields of Note

        return super().save(*args, **kwargs)
