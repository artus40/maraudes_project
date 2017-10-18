from django.urls import reverse
from django import views

from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

class Index(views.generic.TemplateView):

    template_name = "index.html"
    app_menu = None
    header = ('La Maraude ALSA', 'accueil')

    http_method_names = ['get',]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context



def _get_entry_point(user):
    from utilisateurs.models import Maraudeur
    if isinstance(user, Maraudeur):
        return reverse('maraudes:index')
    else:
        return reverse('index')

def login_view(request):
    if request.method == 'GET':
        return HttpResponsePermanentRedirect('/')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            next = request.POST.get('next', None)
            if not next:
                next = _get_entry_point(user)
            messages.success(request, "%s, vous êtes connecté !" % user)
            return HttpResponseRedirect(next)
        else:
            messages.error(request, "Le nom d'utilisateur et/ou le mot de passe sont incorrects !")
            return HttpResponseRedirect('/')
            
