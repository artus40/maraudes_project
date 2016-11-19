from django.shortcuts import render, reverse
from django.views import generic
from django.utils import timezone

from sujets.models import Sujet
from .forms import *
from notes.mixins import NoteFormMixin
from notes.forms import AutoNoteForm
# Create your views here.
from utilisateurs.models import Maraudeur
from website import decorators as website
suivi = website.app_config(
                    name="suivi",
                    groups=[Maraudeur],
                    menu=["suivi/menu/sujets.html"],
                    admin_menu=["suivi/menu/admin_sujets.html"],
                    ajax=False,
                )



@suivi
class IndexView(NoteFormMixin, generic.TemplateView):
    class PageInfo:
        title = "Suivi des bénéficiaires"
        header = "Suivi"
        header_small = "Tableau de bord"
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

@suivi
class SujetListView(generic.ListView):
    class PageInfo:
        title = "Sujet - Liste des sujets"
        header = "Liste des sujets"
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

# Import app_config from 'sujets' application, using
# its admin_menu option
from sujets.views import sujets
@sujets
class SuiviSujetView(NoteFormMixin, generic.DetailView):
    class PageInfo:
        title = "Sujet - {{sujet}}"
        header = "{{sujet}}"
        header_small = "suivi"
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
