from django.forms import ModelForm

from .models import Sujet

class SujetCreateForm(ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']
