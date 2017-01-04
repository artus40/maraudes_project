#-*- coding:utf-8 -*-

from django import template
from django.urls import reverse

register = template.Library()


class NavbarNode(template.Node):
    
    def get_apps(self):
        from navbar.navbar import registered
        if not registered:
            print('WARNING: No app registered into "navbar" module')
        print('getting registered apps:', registered)
        return registered

    def get_template(self):
        return template.loader.get_template('navbar/layout.html')

    def render(self, context):
        apps = self.get_apps()
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



