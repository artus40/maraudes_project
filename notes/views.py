from django.shortcuts import render, redirect, reverse
from django.views import View, generic
from django.utils import timezone

from .models import Sujet
from .forms import SujetCreateForm, SelectSujetForm, AutoNoteForm
from .mixins import NoteFormMixin
from .apps import notes

from maraudes.compte_rendu import CompteRendu

# Create your views here.

@notes.using(title=("Tableau de bord",))
class IndexView(generic.TemplateView):

    #TemplateView
    template_name = "notes/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        return context


@notes.using(title=('{{maraude.date}}', 'compte-rendu'))
class MaraudeDetailsView(generic.DetailView):
    """ Vue détaillé d'un compte-rendu de maraude """

    model = CompteRendu
    context_object_name = "maraude"
    template_name = "maraudes/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.get_observations()
        return context



class ListView(generic.ListView):
    paginate_by = 30

    cell_template = None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_cell_template"] = self.cell_template
        return context


class MaraudeListView(ListView):
    """ Vue de la liste des compte-rendus de maraude """

    model = CompteRendu
    template_name = "notes/liste_maraudes.html"
    cell_template = "notes/table_cell_maraudes.html"

    def get_queryset(self):
        current_date = timezone.localtime(timezone.now()).date()
        qs = super().get_queryset().filter(
                                        date__lte=current_date
                                    ).order_by('-date')

        filtre = self.request.GET.get('filter', None)
        if filtre == "month-only":
            return qs.filter(date__month=current_date.month)
        #Other cases...
        else:
            return qs


class SujetListView(ListView):
    #ListView
    model = Sujet
    template_name = "notes/liste_sujets.html"
    cell_template = "notes/table_cell_sujets.html"

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



@notes.using(title=('{{sujet}}', 'notes'))
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
### Webpage config
from utilisateurs.models import Maraudeur
from website.decorators import Webpage
sujets = Webpage( "sujets", menu=False, defaults={
                        'restricted': [Maraudeur],
                        'ajax': True,
                        }
                    )


@sujets.using(title=('{{object}}', 'details'))
class SujetDetailsView(generic.DetailView):
    #DetailView
    template_name = "notes/sujet_details.html"
    model = Sujet


@sujets
class SujetUpdateView(generic.edit.UpdateView):
    #UpdateView
    template_name = "notes/sujet_update.html"
    model = Sujet
    fields = '__all__'


@sujets
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


