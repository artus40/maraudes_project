from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from .models import Sujet

import datetime

current_year = datetime.date.today().year
YEAR_CHOICE = (year - 2 for year in range(current_year, current_year + 10))

class SujetCreateForm(ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']
        widgets = {
            'premiere_rencontre': SelectDateWidget( empty_label=("Année", "Mois", "Jour"),
                                                    years = YEAR_CHOICE,
                                                    ),
        }
