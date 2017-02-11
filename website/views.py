from django.shortcuts import redirect
from django.urls import reverse
from django import views
from .mixins import WebsiteTemplateMixin

from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

class Index(WebsiteTemplateMixin, views.generic.TemplateView):

    template_name = "main.html"
    app_menu = None
    header = ('La Maraude ALSA', 'accueil')
    class PageInfo:
        title = "La maraude ALSA"
        header = "La Maraude ALSA"
        header_small = "accueil"

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
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect('/')
