from django.shortcuts import redirect
from django import views
from .mixins import WebsiteTemplateMixin


class Index(WebsiteTemplateMixin, views.generic.TemplateView):

    template_name = "main.html"
    app_menu = [] #TODO: fix this !
    class PageInfo:
        title = "La maraude ALSA"
        header = "La Maraude ALSA"
        header_small = "informations"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return super().get(request, *args, **kwargs)
        else:
            return redirect('maraudes:index')


