from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from .models import Sujet

class SujetCreateForm(ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']
        widgets = {
            'premiere_rencontre': SelectDateWidget(empty_label=("Année", "Mois", "Jour")),
        }
