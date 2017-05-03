from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Maraudeur

class MaraudeurMixin(UserPassesTestMixin):

    def test_func(self):
        return isinstance(self.request.user, Maraudeur)
