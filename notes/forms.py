import datetime

from .models import Note, Sujet
from utilisateurs.models import Professionnel

from django import forms
from django_select2.forms import Select2Widget


# NOTES
class NoteForm(forms.ModelForm):
    """ Generic Note form """
    class Meta:
        model = Note
        fields = ['sujet', 'text', 'created_by', 'created_date', 'created_time']
        widgets = {
            'sujet': Select2Widget(),
            'text': forms.Textarea(
                attrs={'rows': 4}
            ),
        }


class SimpleNoteForm(forms.ModelForm):
    """ Simple note with only 'sujet' and 'text' fields.

        Usefull with children of 'Note' that defines all 'note_*'
        special methods.
    """
    class Meta(NoteForm.Meta):
        fields = ['sujet', 'text']


class UserNoteForm(NoteForm):
    """ Form that sets 'created_by' with current user id.

        It requires 'request' object at initialization
    """
    class Meta(NoteForm.Meta):
        fields = ['sujet', 'text', 'created_date', 'created_time']

    def __init__(self, **kwargs):
        request = kwargs.pop('request')
        super().__init__(**kwargs)
        try:
            self.author = Professionnel.objects.get(pk=request.user.pk)
        except Professionnel.DoesNotExist:
            msg = "%s should not have been initiated with '%s' user" % (self, request.user)
            raise RuntimeError(msg)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_by = self.author
        if commit:
            instance.save()
        return instance


class AutoNoteForm(UserNoteForm):
    class Meta(UserNoteForm.Meta):
        fields = ['text']

    def __init__(self, **kwargs):
        self.sujet = kwargs.pop('sujet')
        super().__init__(**kwargs)

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.sujet = self.sujet
        if commit:
            inst.save()
        return inst


# SUJETS
current_year = datetime.date.today().year
YEAR_CHOICE = tuple(year - 2 for year in range(current_year, current_year + 10))


class SujetCreateForm(forms.ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']
        widgets = {
            'premiere_rencontre': forms.SelectDateWidget(
                empty_label=("Année", "Mois", "Jour"),
                years=YEAR_CHOICE,
            ),
        }


class SelectSujetForm(forms.Form):

    sujet = forms.ModelChoiceField(queryset=Sujet.objects.all(), widget=Select2Widget)
