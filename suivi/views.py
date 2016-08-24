from django.shortcuts import render, reverse
from django.views import generic
from django.utils import timezone

from sujets.models import Sujet
from .forms import *
from notes.mixins import NoteFormMixin
from notes.forms import AutoNoteForm
from .search import SearchFormMixin, SearchFormProcessView
# Create your views here.
from website import decorators as website
webpage = website.webpage(
                    ajax=False,
                    permissions=['sujets.view_sujets'],
                    app_menu=["suivi/menu_sujets.html"]
                )



@webpage
class IndexView(SearchFormMixin, NoteFormMixin, generic.TemplateView):
    class PageInfo:
        title = "Suivi des bénéficiaires"
        header = "Suivi"
        header_small = "Tableau de bord"
    #NoteFormMixin
    forms = {
        'appel': AppelForm,
        'signalement': SignalementForm,
    }
    success_url = "/suivi/"
    #FormView
    template_name = "suivi/index.html"
    def get_initial(self):
        return {'created_date': timezone.localtime(timezone.now()).date(),
                'created_time': timezone.localtime(timezone.now()).time()}




@webpage
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_menu("sujets/menu_sujet.html")
    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['notes'] = self.object.notes.by_date(reverse=True)
        return context
