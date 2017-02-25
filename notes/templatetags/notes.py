from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag("notes/table_inline.html")
def inline_table(note, header=None):
    from maraudes.models import Maraude
    bg_color, bg_label_color = note.bg_colors

    if not header:
        header = "date"
    if not header in ['sujet', 'date']:
        raise ValueError('header must be "sujet" or "date"')

    if header == "date":
        header_field = "created_date"
        try:
            maraude = Maraude.objects.get(date=note.created_date)
            link = reverse('maraudes:details', kwargs={'pk': maraude.pk})
        except Maraude.DoesNotExist:
            link = None
    elif header == "sujet":
        header_field = "sujet"
        link = reverse("suivi:details", kwargs={'pk': note.sujet.pk})

    header = getattr(note, header_field)

    return {
        'header': header,
        'link': link,
        'small': note.child_class.__qualname__,
        'bg_color': bg_color or "default",
        'bg_label_color': bg_label_color or "info",
        'labels': note.labels,
        'text': note.text,
    }
