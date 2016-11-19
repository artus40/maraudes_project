from django import template

register = template.Library()

@register.inclusion_tag("notes/table_inline.html")
def inline_table(note, header=None):
    bg_color, bg_label_color = note.bg_colors

    if not header:
        header = "date"
    if not header in ['sujet', 'date']:
        raise ValueError('header must be "sujet" or "date"')

    if header == "date":
        header_field = "created_date"
    elif header == "sujet":
        header_field = "sujet"

    return {
        'header': getattr(note, header_field),
        'small': note.child_class.__qualname__,
        'bg_color': bg_color or "default",
        'bg_label_color': bg_label_color or "info",
        'labels': note.labels,
        'text': note.text,
    }
