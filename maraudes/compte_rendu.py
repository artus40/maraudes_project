from .models import Maraude

from collections import OrderedDict

class CompteRendu(Maraude):
    """ Proxy for Maraude objects.
        Gives access to related Observation and Rencontre
    """

    def __iter__(self):
        return self._iter()

    def reversed(self):
        return self._iter(order="-heure_debut")

    def _iter(self, order="heure_debut"):
        for r in self.rencontres.get_queryset().order_by(order):
            yield (r, [o for o in r.observations.all()])

    def as_list(self, **kwargs):
        return [t for t in self._iter(**kwargs)]

    def as_dict(self, key_field="lieu"):
        """ Returns an 'OrderedDict' with given 'key_field' value as keys and
            the corresponding (rencontre, observations) tuple
        """
        condensed = OrderedDict()
        for r, obs in self.__iter__():
            val = getattr(r, key_field, None)
            if not val:
                pass
            if not val in condensed:
                condensed[val] = [(r, obs)]
            else:
                condensed[val].append((r, obs))
        return condensed

    class Meta:
        proxy = True


