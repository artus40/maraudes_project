from django.db.models import Manager

import datetime
from django.utils import timezone
from django.utils.functional import cached_property


class MaraudeManager(Manager):
    """ Manager for Maraude objects """

    def all_of(self, maraudeur):
        """ Retourne la liste des maraudes de 'maraudeur' """
        # Le référent ne peut participer qu'en tant que référent
        if maraudeur.is_superuser:
            return self.get_queryset().filter(referent=maraudeur.id)

        # Un maraudeur peut occasionnellement être référent
        maraudes_ref = self.get_queryset().filter(referent=maraudeur.id)
        maraudes_bin = self.get_queryset().filter(binome=maraudeur.id)
        if not maraudes_ref:
            return maraudes_bin

        cursor = 0
        complete_list = []
        for i, m in enumerate(maraudes_bin):
            if cursor >= 0 and maraudes_ref[cursor].date < m.date:
                complete_list.append(maraudes_ref[cursor])
                complete_list.append(m)
                if cursor < len(maraudes_ref) - 1:
                    cursor += 1
                else:
                    cursor = -1
            else:
                complete_list.append(m)
        # Don't lose remaining items of maraudes_ref
        if cursor >= 0:
            complete_list += maraudes_ref[cursor:]

        return complete_list


    def get_next_of(self, maraudeur):
        """ Retourne la prochaine maraude de 'maraudeur' """
        return self.all_of(maraudeur).filter(
                            date__gte=datetime.date.today()
                        ).order_by(
                            'date'
                        ).first()

    def get_future(self):
        """ Retourne la liste des prochaines maraudes """
        return self.get_queryset().filter(
                            date__gte=datetime.date.today()
                        ).order_by(
                            'date'
                        )

    def get_past(self):
        """ Retourne la liste des maraudes passées """
        return self.get_queryset().filter(
                            date__lt=datetime.date.today()
                        ).order_by(
                            'date'
                        )

    @cached_property
    def next(self):
        """ Prochaine maraude """
        return self.get_future().first()

    @cached_property
    def last(self):
        """ Dernière maraude """
        return self.get_past().last()

    @cached_property
    def in_progress(self):
        """ Retourne la maraude en cours, ou None """
        d, t = timezone.now().date(), timezone.now().time()

        # Prendre le jour précédent s'il est entre minuit et 2h du matin
        depassement = False
        if t <= datetime.time(2):
            d = d - datetime.timedelta(days=1)
            depassement = True

        maraude_du_jour = self.get(date=d)

        if maraude_du_jour:
            if depassement or t >= maraude_du_jour.heure_debut:
                return maraude_du_jour
        return None



class ObservationManager(Manager):

    def get_for_sujet(self, sujet):
        return self.filter(sujet=sujet)

    def get_first_for_sujet(self, sujet):
        return self.filter(sujet=sujet).order_by('date').first()