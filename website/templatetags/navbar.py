#-*- coding:utf-8 -*-

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe


register = template.Library()


class NavbarNode(template.Node):

    _apps = None

    def get_menus(self, view, user):
        if not self._apps:
            from website.navbar import registered
            if not registered:
                print('WARNING: No app registered into "navbar" module')
            self._apps = registered.copy()
        return [app_menu(view, user) for app_menu in self._apps]

    def get_template(self):
        return template.loader.get_template('navbar/layout.html')

    def render(self, context):
        request = context.get('request')
        user, view = context.get('user'), context.get('view')
        apps = self.get_menus(view, user)
        # Add user menu
        context = template.Context({
            'apps': apps,
            'user': user,
            'user_group': context.get('user_group', None),
            'next': context.get('next', None),

        })
        return self.get_template().render(context, request)

@register.tag
def navbar(parser, token):
    return NavbarNode()

@register.inclusion_tag("navbar/app-menu.html")
def navbar_menu(app_menu):
    return {
        'active': app_menu.is_active,
        'header': app_menu.header,
        'links': app_menu.links,
    }


@register.simple_tag(takes_context=True)
def active(context, namespace=None, viewname=None):
    try:
        (cur_namespace, cur_viewname) = context.request.resolver_match.view_name.split(":")
    except:
        (cur_namespace, cur_viewname) = (None, context.request.resolver_match.view_name)

    if namespace == cur_namespace:
        if not viewname or viewname == cur_viewname:
            return mark_safe("class=\"active\"")
    return ""
