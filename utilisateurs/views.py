from django.views import generic

from .apps import utilisateurs
from .models import Professionnel

@utilisateurs
class UtilisateurView(generic.DetailView):

    template_name = "utilisateurs/details.html"
    model = Professionnel

    def get_object(self):
        qs = self.get_queryset()
        return qs.filter(pk=self.request.user.pk)
