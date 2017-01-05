#-*- coding:utf-8 -*-

from navbar import ApplicationMenu

class SuiviMenu(ApplicationMenu):

    name="suivi"
    header= ("Suivi", 'suivi:index', 'eye-open')

    def get_links(self):
        return [ ('Liste des sujets', 'suivi:liste', 'list'), ]

    def get_dropdowns(self, view):
        print('get dropdowns using', view)
        return []
