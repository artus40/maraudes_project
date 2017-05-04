import logging

from django.shortcuts import redirect, reverse
from django.views import generic
from django.utils import timezone

from utilisateurs.mixins import MaraudeurMixin
from maraudes.models import Maraude, CompteRendu
from .models import Sujet
from .forms import SujetCreateForm, AutoNoteForm
from .mixins import NoteFormMixin


logger = logging.getLogger(__name__)
# Create your views here.

class IndexView(MaraudeurMixin, generic.TemplateView):
    template_name = "notes/index.html"

class Filter:

    def __init__(self, title, name, filter_func):
        self.title = title
        self.parameter_name = name
        self.active = False
        self._filter_func = filter_func

    def filter(self, qs):
        return self._filter_func(qs)



class ListView(MaraudeurMixin, generic.ListView):
    """ Base ListView for Maraude and Sujet lists """
    paginate_by = 30
    cell_template = None

    filters = []
    active_filter = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filters = {}

        if self.filters:
            for i, (title, func) in enumerate(self.filters):
                _id = "filter_%i" % i
                self._filters[_id] = Filter(title, _id, func)

    def get(self, request, **kwargs):
        filter_name = self.request.GET.get('filter', None)
        if filter_name:
            self.active_filter = self._filters.get(filter_name, None)
            if self.active_filter:
                self.active_filter.active = True

        return super().get(request, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.active_filter:
            qs = self.active_filter.filter(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = self._filters.values()
        context["table_cell_template"] = self.cell_template
        return context


class MaraudeListView(ListView):
    """ Vue de la liste des compte-rendus de maraude """

    model = CompteRendu
    template_name = "notes/liste_maraudes.html"
    cell_template = "notes/table_cell_maraudes.html"

    filters = [
        ("Ce mois-ci", lambda qs: qs.filter(date__month=timezone.now().date().month)),
        ("Test", lambda qs: qs)
    ]


class SujetListView(ListView):
    #ListView
    model = Sujet
    template_name = "notes/liste_sujets.html"
    cell_template = "notes/table_cell_sujets.html"

    filters = [
        ("Rencontré(e)s cette année", lambda qs: qs.filter(premiere_rencontre__year=timezone.now().date().year)),
    ]

    def post(self, request, **kwargs):
        from watson import search as watson
        search_text = request.POST.get('q')
        results = watson.filter(Sujet, search_text)
        #logger.warning("SEARCH for %s : %s" % (search_text, results))
        if results.count() == 1:
            return redirect(results[0].get_absolute_url())
        self.queryset = results
        return self.get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_text'] = self.request.POST.get('q', None)
        return context




class CompteRenduDetailsView(generic.DetailView):
    """ Vue détaillé d'un compte-rendu de maraude """

    model = CompteRendu
    context_object_name = "maraude"
    template_name = "maraudes/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.get_observations()
        return context


class SuiviSujetView(NoteFormMixin, generic.DetailView):
    #NoteFormMixin
    forms = {
        'note': AutoNoteForm,
        }
    def get_success_url(self):
        return reverse('notes:details', kwargs={'pk': self.get_object().pk})
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


### Sujet Management Views

class SujetDetailsView(generic.DetailView):
    #DetailView
    template_name = "notes/sujet_details.html"
    model = Sujet



class SujetUpdateView(generic.edit.UpdateView):
    #UpdateView
    template_name = "notes/sujet_update.html"
    model = Sujet
    fields = '__all__'



class SujetCreateView(generic.edit.CreateView):
    #CreateView
    template_name = "notes/sujet_create.html"
    form_class = SujetCreateForm
    def post(self, request, *args, **kwargs):
        if 'next' in self.request.POST:
            self.success_url = self.request.POST["next"]
        return super().post(self, request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:   context['next'] = self.request.GET['next']
        except:context['next'] = None
        return context


