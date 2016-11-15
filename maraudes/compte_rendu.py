from .models import Maraude

from collections import OrderedDict

import datetime

def split_by_12h_blocks(iterable):
    """ Move object with given 'field' time under 12:00 to the end of stream.
        Apart from this, order is untouched.
    """
    to_end = []
    for note in iterable:
        if getattr(note, "created_time") <= datetime.time(12):
            to_end.append(note)
        else:
            yield note

    for note in to_end:
        yield note

class CompteRendu(Maraude):
    """ Proxy for Maraude objects.
        Gives access to related Observation and Rencontre
    """

    def rencontre_count(self):
        return self.rencontres.count()

    def observation_count(self):
        count = 0
        for r in self:
            count += r.observations.count()
        return count

    def get_observations(self, order="heure_debut", reverse=False):
        """ Returns list of all observations related to this instance """
        observations = []
        for r in self._iter(order=order, reverse=reverse):
            observations += r.observations.get_queryset()
        return list(split_by_12h_blocks(observations))

    def __iter__(self):
        """ Iterates on related 'rencontres' objects using default ordering """
        return self._iter()

    def reversed(self, order="heure_debut"):
        return self._iter(order=order, reverse=True)

    def _iter(self, order="heure_debut", reverse=False):
        """ Iterator on related 'rencontre' queryset.

            Optionnal :
            - order : order by this field, default: 'heure_debut'
            - reversed : reversed ordering, default: False
        """
        if reverse:
            order = "-" + order
        for rencontre in self.rencontres.get_queryset().order_by(order):
            yield rencontre

    def as_list(self, **kwargs):
        return [r for r in self._iter(**kwargs)]

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


