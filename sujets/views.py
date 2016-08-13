from django.shortcuts import render

from django.views import generic
from website import decorators as website

from .models import Sujet

from django.forms import ModelForm


webpage = website.webpage(
                    ajax=True,
                    permissions=['sujets.view_sujets'],
                    app_name="suivi",
                    app_menu=["suivi/menu_sujets.html", "suivi/menu_administration.html"]
                )
# Create your views here.

# TODO: deal with setting an active_app name other than module name

@webpage
class SujetDetailsView(generic.DetailView):
    template_name = "sujets/sujet_details.html"
    model = Sujet

    class PageInfo:
        title = "Sujet - {{ sujet }}"
        header = "{{ sujet }}"
        header_small = "suivi"

@webpage
class SujetListView(generic.ListView):
    model = Sujet
    template_name = "sujets/sujet_liste.html"

    class PageInfo:
        title = "Sujet - Liste des sujets"
        header = "Liste des sujets"

@webpage
class SujetUpdateView(generic.edit.UpdateView):
    template_name = "sujets/sujet_update.html"
    model = Sujet
    fields = '__all__'

    class PageInfo:
        title = "Mise à jour - {{sujet}}"
        header = "{{sujet}}"
        header_small = "mise à jour"



class SujetCreateForm(ModelForm):
    class Meta:
        model = Sujet
        fields = ['nom', 'surnom', 'prenom', 'genre', 'premiere_rencontre']


@website.webpage(ajax=True, permissions=['sujets.add_sujet'], app_name="suivi")
class SujetCreateView(generic.edit.CreateView):
    template_name = "sujets/sujet_create.html"
    form_class = SujetCreateForm

    class PageInfo:
        title = "Nouveau sujet"
        header = "Nouveau sujet"

    def post(self, request, *args, **kwargs):
        if 'next' in self.request.POST:
            self.success_url = self.request.POST["next"]
        return super().post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['next'] = self.request.GET['next']
        except:
            context['next'] = None
        return context
