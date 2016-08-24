from .notes import *
from notes.forms import *
from sujets.models import Sujet, GENRE_CHOICES
from django import forms

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
