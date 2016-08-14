from django.shortcuts import render
from django.views import generic

from .models import Sujet
from .forms import SujetCreateForm

### Webpage config
from website import decorators as website
webpage = website.webpage(
                    ajax=True,
                    permissions=['sujets.view_sujets'],
                    app_name="suivi",
                    app_menu=["sujets/menu_sujet.html"]
                )
### Views

@webpage
class SujetDetailsView(generic.DetailView):
    class PageInfo:
        title = "Sujet - {{ sujet }}"
        header = "{{ sujet }}"
        header_small = "suivi"
    #DetailView
    template_name = "sujets/sujet_details.html"
    model = Sujet



@webpage
class SujetListView(generic.ListView):
    class PageInfo:
        title = "Sujet - Liste des sujets"
        header = "Liste des sujets"
    #ListView
    model = Sujet
    template_name = "sujets/sujet_liste.html"
    paginate_by = 10
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_menu = ["suivi/menu_sujets.html"]



@webpage
class SujetUpdateView(generic.edit.UpdateView):
    class PageInfo:
        title = "Mise à jour - {{sujet}}"
        header = "{{sujet}}"
        header_small = "mise à jour"
    #UpdateView
    template_name = "sujets/sujet_update.html"
    model = Sujet
    fields = '__all__'



@webpage
class SujetCreateView(generic.edit.CreateView):
    class PageInfo:
        title = "Nouveau sujet"
        header = "Nouveau sujet"
    # Special permissions
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permissions += ['sujets.add_sujet']
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
