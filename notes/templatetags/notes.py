from notes.models import Note

from django import template

register = template.Library()

@register.inclusion_tag("notes/table_inline.html")
def inline_table(note):
    bg_color, bg_label_color = note.bg_colors
    return {
        'header': note.created_date,
        'small': note.child_class.__qualname__,
        'bg_color': bg_color or "default",
        'bg_label_color': bg_label_color or "info",
        'labels': note.labels,
        'text': note.text,
    }
