from django.contrib.auth.backends import ModelBackend

from utilisateurs.models import Maraudeur

class MyBackend(ModelBackend):

    def authenticate(self, **kwargs):
        print('authenticate using MyBackend')
        return super().authenticate(**kwargs)

    def get_user(self, user_id):
        """ Retourne la classe enfant de l'utilisateur connecté
            s'il en a une, sinon le User par défaut.
        """
        print('use MyBackend: get_user', user_id)
        try:
            user = Maraudeur.objects.get(pk=user_id)
        except Maraudeur.DoesNotExist:
            print('no Maraudeur found. Using base user class')
            user = super().get_user(user_id)
        print("found:", user, user.__class__)
        return user

    def has_perm(self, *args, **kwargs):
        print('call has_perm', args, kwargs)
        return super().has_perm(*args, **kwargs)
