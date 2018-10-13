#-*- coding:utf-8 -*-

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, namespace=None, viewname=None, append=False):
    try:
        (cur_namespace, cur_viewname) = context.request.resolver_match.view_name.split(":")
    except:
        (cur_namespace, cur_viewname) = (None, context.request.resolver_match.view_name)

    string = "class=\"active shadow\"" if not append else "active shadow"

    if namespace == cur_namespace:
        if not viewname or viewname == cur_viewname:
            return mark_safe(string)
    return ""
