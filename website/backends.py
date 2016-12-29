from django.contrib.auth.backends import ModelBackend

from utilisateurs.models import Maraudeur


def user_models():
    return (Maraudeur,)

class MyBackend(ModelBackend):

    def get_user(self, user_id):
        """ Essaye de récupérer une classe enfant de User existante, telle que
            définie dans 'utilisateurs.models'. Fallback to default user.
        """
        for user_model in user_models():
            try:
                return user_model.objects.get(pk=user_id)
            except user_model.DoesNotExist:
                print('Tried %s.' % user_model.__class__)
        return super().get_user(user_id)

    def has_perm(self, *args, **kwargs):
        print('call has_perm', args, kwargs)
        return super().has_perm(*args, **kwargs)
