from django import template
from django.utils.html import format_html
register = template.Library()

@register.filter
def as_icon(value):
    icons = {True: "circle-check",
            False: "circle-x",
            None: "question-mark"
            }
    if not value in icons:
        raise ValueError(value, 'is not a boolean or empty value !')
    else:
        return format_html('<span class="oi oi-{}" aria-hidden="true"></span>', icons[value])
