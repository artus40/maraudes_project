from django import forms
from django.db.utils import OperationalError

from .models import FicheStatistique

class StatistiquesForm(forms.ModelForm):

    class Meta:
        model = FicheStatistique
        exclude = ["sujet"]


def get_year_range():
    qs = FicheStatistique.objects.filter(
                sujet__premiere_rencontre__isnull=False
            ).order_by(
                'sujet__premiere_rencontre'
            )
    year = lambda f: f.sujet.premiere_rencontre.year
    
    # Need to call exists() in a try block
    # to avoid raising exception on first migration
    try:
        qs_is_not_empty = qs.exists()
    except OperationalError:
        qs_is_not_empty = False
        
    if qs_is_not_empty:
        return range(year(qs.first()), year(qs.last()) + 1)
    else:
        return ()

class SelectRangeForm(forms.Form):

    year = forms.ChoiceField(label="Année", choices=[(0, 'Toutes')] + [(i, str(i)) for i in get_year_range()])
    month = forms.ChoiceField(label="Mois",
                    choices=[(0, 'Tous'),
                        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
                        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
                        (9, 'Septembre'),(10, 'Octobre'),(11, 'Novembre'),(12, 'Décembre')
                    ],
                )
