from django.views import generic

from .models import Professionnel

class UtilisateurView(generic.DetailView):

    template_name = "utilisateurs/details.html"
    model = Professionnel

    def get_object(self):
        qs = self.get_queryset()
        return qs.filter(pk=self.request.user.pk)
