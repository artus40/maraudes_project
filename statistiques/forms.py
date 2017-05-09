from django import forms
from .models import FicheStatistique

class StatistiquesForm(forms.ModelForm):

    class Meta:
        model = FicheStatistique
        exclude = ["sujet"]
