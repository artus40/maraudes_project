from django.shortcuts import render

from django.views import generic
from website import views

from .models import Sujet

from django.forms import ModelForm

# Create your views here.

class SujetsView(views.WebsiteProtectedMixin):

    class PageInfo:
        title = "Sujets"

    def get_active_app(self):
        return super(views.WebsiteProtectedMixin, self).get_active_app(app_name='suivi')



class SujetDetailsView(SujetsView, generic.DetailView):
    template_name = "sujets/sujet_details.html"
    model = Sujet

    class PageInfo:
        title = "Sujet - {{ sujet }}"
        header = "{{ sujet }}"
        header_small = "suivi"

class SujetListView(SujetsView, generic.ListView):
    model = Sujet
    template_name = "sujets/sujet_liste.html"

    class PageInfo:
        title = "Sujet - Liste des sujets"
        header = "Liste des sujets"


class SujetUpdateView(SujetsView, generic.edit.UpdateView):
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



class SujetCreateView(views.WebsiteProtectedWithAjaxMixin, generic.edit.CreateView):
    template_name = "sujets/sujet_create.html"
    form_class = SujetCreateForm

    class PageInfo:
        title = "Nouveau sujet"
        header = "Nouveau sujet"

    permissions = ['sujets.view_sujets', 'sujets.add_sujet']

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

    #Hack
    get_active_app = SujetsView.get_active_app
