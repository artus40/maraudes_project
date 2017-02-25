import datetime
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django_select2.forms import Select2Widget

from .models import Sujet

current_year = datetime.date.today().year
YEAR_CHOICE = tuple(year - 2 for year in range(current_year, current_year + 10))

class SujetCreateForm(forms.ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']
        widgets = {
            'premiere_rencontre': SelectDateWidget( empty_label=("Année", "Mois", "Jour"),
                                                    years = YEAR_CHOICE,
                                                    ),
        }

class SelectSujetForm(forms.Form):

    sujet = forms.ModelChoiceField(queryset=Sujet.objects.all(), widget=Select2Widget)
