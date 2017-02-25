from django.shortcuts import render, redirect
from django.views import View, generic

from .models import Sujet
from .forms import SujetCreateForm, SelectSujetForm

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

from .actions import merge_two
from django.shortcuts import redirect
from django.contrib import messages

@sujets.using(title=('Fusionner',))
class MergeView(generic.DetailView, generic.FormView):
    """ Implement actions.merge_two as a view """
    
    template_name = "sujets/sujet_merge.html"
    model = Sujet
    form_class = SelectSujetForm

    def form_valid(self, form):
        slave = self.get_object()
        master = form.cleaned_data['sujet']
        try:
            merge_two(master, slave)
        except:
            messages.error(self.request, "La fusion vers %s a échoué !" % master)
            return redirect(slave)
        messages.success(self.request, "%s vient d'être fusionné" % slave)        
        return redirect(master)
