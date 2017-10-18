from django.views import generic
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from maraudes.models import Maraude

from .models import Professionnel
from .mixins import MaraudeurMixin

class UtilisateurView(MaraudeurMixin, generic.DetailView):

    template_name = "utilisateurs/details.html"
    model = Professionnel
    form = None
    def get(self, request, **kwargs):
        if not self.form:
            self.form = PasswordChangeForm(request.user)
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Votre mot de passe a été mis à jour!')
        else:
            self.form = form
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous')
        
        return self.get(request, **kwargs)


    def get_object(self):
        qs = self.get_queryset()
        return qs.filter(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_change_form'] = self.form
        
        user_maraudes = Maraude.objects.all_of(self.request.user)
        context['nbr_maraudes'] = user_maraudes.count()
        
        current_year = timezone.localtime(timezone.now()).date().year
        context['nbr_maraudes_annee'] = user_maraudes.filter(date__year=current_year).count()
        
        return context
