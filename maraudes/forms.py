from django import forms
from django.forms import inlineformset_factory
from notes.forms import NoteForm
# Models
from .models import Maraude, Rencontre
from .notes import Observation, Signalement


class MaraudeAutoDateForm(forms.ModelForm):
    """ Maraude ModelForm with disabled 'date' field """
    class Meta:
        model = Maraude
        fields = ['date', 'heure_debut', 'referent', 'binome']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].disabled = True



class RencontreForm(forms.ModelForm):
    class Meta:
        model = Rencontre
        fields = ['lieu', 'heure_debut', 'duree']


class SignalementForm(NoteForm):

    class Meta:
        model = Signalement
        fields = ['source', 'created_date', 'created_time', 'sujet', 'text']


ObservationInlineFormSet = inlineformset_factory(   Rencontre, Observation,
                                                    form=NoteForm,
                                                    extra = 0,
                                                    min_num = 1,
                                                    )

RencontreInlineFormSet = inlineformset_factory(
                                Maraude, Rencontre,
                                form = RencontreForm,
                                extra = 0,
                                )

ObservationInlineFormSetNoExtra = inlineformset_factory(
                                Rencontre, Observation,
                                form = NoteForm,
                                extra = 0
                                )

class MonthSelectForm(forms.Form):

    month = forms.ChoiceField(
                    choices=[
                        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
                        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
                        (9, 'Septembre'),(10, 'Octobre'),(11, 'Novembre'),(12, 'Décembre')
                    ],
                )
    year = forms.ChoiceField(
                    choices = [(y, y) for y in [2015, 2016, 2017, 2018]]
                )

    def __init__(self, *args, month=None, year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].initial = month
        self.fields['year'].initial = year

