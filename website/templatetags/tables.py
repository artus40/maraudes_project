from django import template
from itertools import zip_longest, islice

register = template.Library()

def get_rows(iterable, cols):
    """ Returns a tuple of rows """
    i = iter(iterable)
    row = tuple(islice(i, cols))
    while row:
        yield row
        row = tuple(islice(i, cols))

@register.inclusion_tag("tables/table.html")
def table(object_list, cols=2, cell_template="tables/table_cell_default.html", header=None):
    """ Render object list in table of given columns number """
    return {
            'cell_template': cell_template,
            'cols_number': cols,
            'header': header,
            'rows': tuple(get_rows(object_list, cols)),
            }

