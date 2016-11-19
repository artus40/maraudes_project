from django.shortcuts import redirect
from django.urls import reverse
from django import views
from .mixins import WebsiteTemplateMixin

from django.contrib.auth.views import login
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

class Index(WebsiteTemplateMixin, views.generic.TemplateView):

    template_name = "main.html"
    app_menu = None

    class PageInfo:
        title = "La maraude ALSA"
        header = "La Maraude ALSA"
        header_small = "accueil"

    def _get_user_entry_point(self):
        # Should find best entry point according to user Group
        return reverse('maraudes:index')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self._get_user_entry_point())
        return super().get(request, *args, **kwargs)



def login_view(request):
    if request.method == 'GET':
        return HttpResponsePermanentRedirect('/')
    elif request.method == 'POST':
        #TODO: authenticate instead of mis-using 'login' view.
        response = login(request)
        return HttpResponseRedirect('/')
