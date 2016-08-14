from django.shortcuts import render

from django.views import generic
from website import decorators as website

from sujets.models import Sujet

# Create your views here.

webpage = website.webpage(
                    ajax=False,
                    permissions=['sujets.view_sujets'],
                    app_menu=["suivi/menu_sujets.html"]
                )



@webpage
class IndexView(generic.TemplateView):
    class PageInfo:
        title = "Suivi des bénéficiaires"
        header = "Suivi"
        header_small = "Tableau de bord"
    #TemplateView
    template_name = "suivi/index.html"


from notes.mixins import NoteFormMixin

@webpage
class SuiviSujetView(NoteFormMixin, generic.DetailView):
    class PageInfo:
        title = "Sujet - {{sujet}}"
        header = "{{sujet}}"
        header_small = "suivi"
    #DetailView
    model = Sujet
    template_name = "suivi/details.html"
    context_object_name = "sujet"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_menu.insert(0, "sujets/menu_sujet.html")
    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['notes'] = self.object.notes.by_date(reverse=True)
        return context
