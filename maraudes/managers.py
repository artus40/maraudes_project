import datetime
from django.utils import timezone
from django.utils.functional import cached_property
from django.db.models import Manager


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

        return maraudes_bin | maraudes_ref

    def get_next_of(self, maraudeur):
        """ Retourne la prochaine maraude de 'maraudeur' """
        return self.all_of(maraudeur).filter(
                            date__gte=datetime.date.today()
                        ).order_by(
                            'date'
                        ).first()

    def get_future(self, date=None):
        """ Retourne la liste des prochaines maraudes """
        if not date:
            date = self.today
        return self.get_queryset().filter(
                            date__gte=date
                        ).order_by(
                            'date'
                        )

    def get_past(self, date=None):
        """ Retourne la liste des maraudes passées """
        if not date:
            date = self.today
        return self.get_queryset().filter(
                            date__lt=date
                        ).order_by(
                            'date'
                        )

    @cached_property
    def today(self):
        return timezone.localtime(timezone.now()).date()

    @cached_property
    def next(self):
        """ Prochaine maraude """
        return self.get_future().first()

    @cached_property
    def last(self):
        """ Dernière maraude """
        return self.get_past().last()

    def get_in_progress(self):
        """ Retourne la maraude en cours, ou None """
        d, t = self.today, timezone.localtime(timezone.now()).time()

        # Prendre le jour précédent s'il est entre minuit et 2h du matin
        depassement = False
        if t <= datetime.time(2):
            d = d - datetime.timedelta(days=1)
            depassement = True

        try:
            maraude_du_jour = self.get(date=d)
            if depassement or t >= maraude_du_jour.heure_debut:
                return maraude_du_jour
            else:
                return None
        except self.model.DoesNotExist:
            return None
