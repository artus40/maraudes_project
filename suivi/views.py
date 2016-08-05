from django.shortcuts import render

from django.views import generic
from website import views

from sujets.models import Sujet

# Create your views here.



class SuivisView(views.WebsiteProtectedMixin):
    title = "Suivi des bénéficiaires"
    header = "Suivi"

    permissions = ['sujets.view_sujets']


class IndexView(SuivisView, generic.TemplateView):
    template_name = "suivis/index.html"
    header_small = "Tableau de bord"


class SuiviSujetView(SuivisView, generic.DetailView):
    model = Sujet
    template_name = "suivis/details.html"
    context_object_name = "sujet"

    def get_context_date(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.all()
        return context