#-*- coding:utf-8 -*-

from django import template
from django.urls import reverse

register = template.Library()

class Link:
    def __init__(self, text, target=None, icon=None):
        self.text = text
        if not target:
            raise TypeError
        try:
            target, kwargs = target
        except ValueError:
            target = target
            kwargs = {}
        assert type(target) == str
        assert type(kwargs) == dict
        self.href = reverse(target, **kwargs)
        self.icon = icon

class Dropdown:
    def __init__(self, header, links):
        self.header = header
        self.links = links
  
class AppMenu:

    def __init__(self, header):
        self.header = Link(header, 'maraudes:index', 'road')
        self.is_active = False
    
    def get_links(self):
        """ Shall be implemented in children. """
        return []

    def get_dropdowns(self):
        """ Shall be implemented in children. """
        return []

    @property
    def links(self):
        return self.get_links()

    @property
    def dropdowns(self):
        return self.get_dropdowns()


class NavbarNode(template.Node):

    def get_template(self):
        return template.loader.get_template('navbar/layout.html')

    def render(self, context):
        apps = [AppMenu('Maraudes'), AppMenu('Test app')]
        # Set active app
        active = context['active_app']
        # Add user menu
        request = context.get('request')
        context = template.Context({
            'apps': apps, 
            'user': context.get('user'),
            'user_group': context.get('user_group', None),
            'next': context.get('next', None),

        })
        print(context)
        return self.get_template().render(context, request)

@register.tag
def navbar(parser, token):
    return NavbarNode()

@register.inclusion_tag("navbar/navbar-menu.html")
def navbar_menu(app_menu):
    return {
        'active': app_menu.is_active,
        'header': app_menu.header,
        'links': app_menu.links,
        'dropdowns': app_menu.dropdowns,
    }



