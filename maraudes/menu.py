#-*- coding:utf-8 -*-

from django.utils.functional import cached_property
from navbar import ApplicationMenu, DropDown

# TODO:
#
# The menu is not yet initialized, 
# We shall find a way to do so, without creating problems
# with the url resolver !
# It cannot be in views.py, maybe when app is ready ?
class DernieresMaraudes(DropDown):
    header = "Dernières maraudes"
    
    count = 4
    @cached_property
    def dernieres_maraudes(self):
        """ Renvoie la liste des 'Maraude' passées et terminées """
        #WARNING: Cached property has become inefficient here !
        print('DEBUG_INFO: cached_property retrieves some data :')
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




class MaraudesMenu(ApplicationMenu):
    name = "maraudes" #Could be set by MenuRegistry metacls
    header = ('Maraudes', 'maraudes:index', 'road')

    def get_links(self):
        return [
                ('Liste des maraudes', 'maraudes:liste', 'list'),
            ]

    def get_dropdowns(self, view):
        return [
            DernieresMaraudes(),
        ]

