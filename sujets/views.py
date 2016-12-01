from django.shortcuts import render, redirect
from django.views import generic

from .models import Sujet
from .forms import SujetCreateForm

### Webpage config
from utilisateurs.models import Maraudeur
from website import decorators as website
sujets = website.app_config(
                    name="suivi",
                    groups=[Maraudeur],
                    menu=["suivi/menu/sujets.html"],
                    admin_menu=["sujets/menu/admin_sujet.html"],
                    ajax=True,
                )
### Views

@sujets
class SujetDetailsView(generic.DetailView):
    class PageInfo:
        title = "Sujet - {{ sujet }}"
        header = "{{ sujet }}"
        header_small = "informations"
    #DetailView
    template_name = "sujets/sujet_details.html"
    model = Sujet






@sujets
class SujetUpdateView(generic.edit.UpdateView):
    class PageInfo:
        title = "Mise à jour - {{sujet}}"
        header = "{{sujet}}"
        header_small = "mise à jour"
    #UpdateView
    template_name = "sujets/sujet_update.html"
    model = Sujet
    fields = '__all__'



@sujets
class SujetCreateView(generic.edit.CreateView):
    class PageInfo:
        title = "Nouveau sujet"
        header = "Nouveau sujet"
    #CreateView
    template_name = "sujets/sujet_create.html"
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
