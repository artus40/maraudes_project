from django.shortcuts import reverse, redirect
from django.views import generic
from django.utils import timezone

from sujets.models import Sujet
from .forms import *
from notes.mixins import NoteFormMixin
from notes.forms import AutoNoteForm
# Create your views here.
from utilisateurs.models import Maraudeur
from website.decorators import Webpage
suivi = Webpage("suivi", {
                        'restricted': [Maraudeur],
                        'ajax': False,
                    }
                )
from suivi.menu import SuiviMenu

from maraudes.compte_rendu import CompteRendu

def derniers_sujets_rencontres():
    """ Renvoie le 'set' des sujets rencontrés dans les deux dernières maraudes """
    sujets = set()

    # Issue: Récupère des comptes-rendus, même s'il n'ont pas été rédigé. Ne devrait pas
    # être un souci si on reste à jour, mais sinon...
    for cr in list(CompteRendu.objects.all())[-2:]:
        for obs in cr.get_observations():
            sujets.add(obs.sujet)
    return sujets



@suivi.using(title=("Suivi", "Tableau de bord"))
class IndexView(NoteFormMixin, generic.TemplateView):
    #NoteFormMixin
    forms = {
        'appel': AppelForm,
        'signalement': SignalementForm,
    }
    def get_initial(self):
        return {'created_date': timezone.localtime(timezone.now()).date(),
                'created_time': timezone.localtime(timezone.now()).time()}
    def get_success_url(self):
        return reverse('suivi:index')
    #TemplateView
    template_name = "suivi/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['derniers_sujets'] = ", ".join(map(str, derniers_sujets_rencontres()))
        return context



@suivi.using(title=('Liste des sujets',))
class SujetListView(generic.ListView):
    #ListView
    model = Sujet
    template_name = "sujets/sujet_liste.html"
    paginate_by = 30

    def post(self, request, **kwargs):
        from watson import search as watson
        search_text = request.POST.get('q')
        results = watson.filter(Sujet, search_text)
        if results.count() == 1:
            return redirect(results[0].get_absolute_url())
        self.queryset = results
        return self.get(request, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_text'] = self.request.POST.get('q', None)
        return context



@suivi.using(title=('{{sujet}}', 'suivi'))
class SuiviSujetView(NoteFormMixin, generic.DetailView):
    #NoteFormMixin
    forms = {
        'note': AutoNoteForm,
        }
    def get_success_url(self):
        return reverse('suivi:details', kwargs={'pk': self.get_object().pk})
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['sujet'] = self.get_object()
        return kwargs
    #DetailView
    model = Sujet
    template_name = "suivi/details.html"
    context_object_name = "sujet"
    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['notes'] = self.object.notes.by_date(reverse=True)
        return context
