from django.contrib.auth.backends import ModelBackend


class MyBackend(ModelBackend):

    def authenticate(self, **kwargs):
        print('use MyBackend')
        return super().authenticate(**kwargs)

    def get_user(self, user_id):
        print('use MyBackend: get_user', user_id)
        return super().get_user(user_id)

    def has_perm(self, *args, **kwargs):
        print('call has_perm', args, kwargs)
        return super().has_perm(*args, **kwargs)
