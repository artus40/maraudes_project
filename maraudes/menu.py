#-*- coding:utf-8 -*-

from navbar import ApplicationMenu, DropDown

# TODO:
#
# The menu is not yet initialized, 
# We shall find a way to do so, without creating problems
# with the url resolver !
# It cannot be in views.py, maybe when app is ready ?

class DernieresMaraudes(DropDown):
    pass



class MaraudesMenu(ApplicationMenu):

    header = ('Maraudes', 'maraudes:index', 'road')

    def get_links(self):
        return [
                ('Liste des maraudes', 'maraudes:list', 'list'),
            ]

    def get_dropdowns(self, view):
        pass

