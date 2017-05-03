from django import template
from itertools import zip_longest

register = template.Library()

def get_columns(iterable, cols):
    cols_len = len(iterable) // cols
    if len(iterable) % cols != 0:
        cols_len += 1
    for i in range(cols):
        yield iterable[i*cols_len:(i+1)*cols_len]

@register.inclusion_tag("tables/table.html")
def table(object_list, cols=2, cell_template="tables/table_cell_default.html"):
    """ Render object list in table of given columns number """
    return {
            'cell_template': cell_template,
            'rows': tuple(zip_longest( *get_columns(object_list, cols),
                                        fillvalue=None
                                        ))
            }

@register.inclusion_tag("tables/header_table.html")
def header_table(object_list, cols=2):
    """ Display object list in table of given columns number """
    return {
            'cols': cols,
            'rows': tuple(zip_longest( *get_columns(object_list, cols),
                                        fillvalue=None
                                        ))
                }
