from django.shortcuts import redirect
from django.urls import reverse
from django import views
from .mixins import WebsiteTemplateMixin

from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
class Index(WebsiteTemplateMixin, views.generic.TemplateView):

    template_name = "main.html"
    app_menu = None
    login_response = None

    class PageInfo:
        title = "La maraude ALSA"
        header = "La Maraude ALSA"
        header_small = "accueil"

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.login_response = login(request)
        return super().dispatch(request, *args, **kwargs)

    def _get_user_entry_point(self):
        # Should find best entry point according to user Group
        return reverse('maraudes:index')

    def post(self, request, *args, **kwargs):
        if hasattr(self.login_response, 'url') and 'next' in self.request.POST:
            return self.login_response
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self._get_user_entry_point())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.login_response.context_data)
        return context


