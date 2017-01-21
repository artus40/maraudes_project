#-*- coding:utf-8 -*-

from website.navbar import DropDown


class DernieresMaraudes(DropDown):
    header = "Dernières maraudes"

    count = 4
    def dernieres_maraudes(self):
        """ Renvoie la liste des 'Maraude' passées et terminées """
        from maraudes.models import Maraude
        return Maraude.objects.get_past().filter(
                                            heure_fin__isnull=False
                                        ).order_by(
                                            '-date'
                                        )[:self.count]

    def get_links(self):
        return [
            (   str(maraude), 
                ('maraudes:details', {'kwargs': {'pk': maraude.pk}}),
                None) for maraude in self.dernieres_maraudes ]

