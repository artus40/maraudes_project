from django import forms
from django.utils import timezone

from django_select2.forms import Select2Widget

# Models
from .models import *
from .notes import *
from notes.forms import UserNoteForm, SimpleNoteForm
from notes.models import Sujet, GENRE_CHOICES


def current_year_range():
    """ Returns a range from year -1 to year + 2 """
    year = timezone.now().date().year
    return (year - 1, year, year + 1, year + 2)



class MaraudeHiddenDateForm(forms.ModelForm):
    class Meta:
        model = Maraude
        fields = ['date', 'heure_debut', 'referent', 'binome']
        widgets = {'date': forms.HiddenInput()}




class RencontreForm(forms.ModelForm):
    class Meta:
        model = Rencontre
        fields = ['lieu', 'heure_debut', 'duree']
        widgets = {
            'lieu': Select2Widget(),
        }


ObservationInlineFormSet = forms.inlineformset_factory(   Rencontre, Observation,
                                                    form=SimpleNoteForm,
                                                    extra = 1,
                                                    )

RencontreInlineFormSet = forms.inlineformset_factory(
                                Maraude, Rencontre,
                                form = RencontreForm,
                                extra = 0,
                                )

ObservationInlineFormSetNoExtra = forms.inlineformset_factory(
                                Rencontre, Observation,
                                form = SimpleNoteForm,
                                extra = 0
                                )



class MonthSelectForm(forms.Form):

    month = forms.ChoiceField(label="Mois",
                    choices=[
                        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
                        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
                        (9, 'Septembre'),(10, 'Octobre'),(11, 'Novembre'),(12, 'Décembre')
                    ],
                )
    year = forms.ChoiceField(label="Année",
                    choices = [(y, y) for y in current_year_range()]
                )

    def __init__(self, *args, month=None, year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].initial = month
        self.fields['year'].initial = year



class AppelForm(UserNoteForm):
    class Meta(UserNoteForm.Meta):
        model = Appel
        fields = ['sujet', 'text', 'entrant', 'created_date', 'created_time']



class SignalementForm(UserNoteForm):

    nom = forms.CharField(64, required=False)
    prenom = forms.CharField(64, required=False)
    age = forms.IntegerField(required=False)
    genre = forms.ChoiceField(choices=GENRE_CHOICES)

    class Meta(UserNoteForm.Meta):
        model = Signalement
        fields = ['text', 'source', 'created_date', 'created_time']

    def clean(self):
        super().clean()
        if not self.cleaned_data['nom'] and not self.cleaned_data['prenom']:
            self.add_error('nom', '')
            self.add_error('prenom', '')
            raise forms.ValidationError("Entrez au moins un nom ou prénom")

    def save(self, commit=True):
        sujet = Sujet.objects.create(
                        nom=self.cleaned_data['nom'],
                        prenom=self.cleaned_data['prenom'],
                        genre=self.cleaned_data['genre'],
                        age=self.cleaned_data['age']
                    )
        instance = super().save(commit=False)
        instance.sujet = sujet
        if commit:
            instance.save()
        return instance
