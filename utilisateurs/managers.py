from django.contrib.auth.models import UserManager

class MaraudeurManager(UserManager):
    """ Manager for Maraudeurs objects.
    """

    def get_referent(self):
        try:
            return self.get(is_superuser=True)
        except self.model.DoesNotExist:
            return None

    def set_referent(self, first_name, last_name):
        maraudeur, created = self.get_or_create(first_name=first_name, last_name=last_name)
        for previous in self.get_queryset().filter(is_superuser=True):
            previous.is_superuser = False
            previous.save()
        maraudeur.is_superuser = True
        maraudeur.save()
        return maraudeur
