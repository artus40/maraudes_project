from django.shortcuts import render, redirect
from django.views import generic

from .models import Sujet
from .forms import SujetCreateForm

### Webpage config
from utilisateurs.models import Maraudeur
from website.decorators import Webpage 
sujets = Webpage( "suivi", menu=False, defaults={
                        'restricted': [Maraudeur],
                        'ajax': True,
                        }
                    )
### Views

@sujets.using(title=('{{object}}', 'details'))
class SujetDetailsView(generic.DetailView):
    #DetailView
    template_name = "sujets/sujet_details.html"
    model = Sujet


@sujets
class SujetUpdateView(generic.edit.UpdateView):
    #UpdateView
    template_name = "sujets/sujet_update.html"
    model = Sujet
    fields = '__all__'


@sujets
class SujetCreateView(generic.edit.CreateView):
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
