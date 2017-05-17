from django.db.models import (Field, CharField, NullBooleanField,
                              Count,
                              )
from graphos.sources.simple import SimpleDataSource
from graphos.renderers import gchart


class PieWrapper(gchart.PieChart):
    """ A wrapper around gchart.PieChart that generates a graph from :

        - a queryset and a model field (NullBooleanField or field with choices)
        - a data object and title
    """

    height=400
    width=800
    labels = {
        NullBooleanField: {True: "Oui", False: "Non", None:"Ne sait pas"},
    }

    def __init__(   self, queryset=None, field=None,
                    data=None, title=None,
                    null_values=[],**kwargs):
        if not data:
            if not isinstance(field, Field):
                raise TypeError(field, 'must be a child of django.models.db.fields.Field !')
            if not queryset:
                raise TypeError("You must give either a queryset and field or data")

            if field.__class__ in PieWrapper.labels:
                labels = PieWrapper.labels[field.__class__]
            elif field.choices:
                labels = dict(field.choices)
            else:
                raise ValueError("Could not guess labels for", field)

            data = ([(field.name, 'count')] + # Headers
                [(labels[item[field.name]],
                  item['nbr']) for item in queryset.values(
                                                    field.name
                                                ).annotate(
                                                    nbr=Count('pk')
                                                ).order_by()
                if (not null_values
                    or item[field] not in null_values)
                ])

        super().__init__(
            SimpleDataSource(
                data=data
                ),
            options={
                'title': getattr(field, 'verbose_name', title),
                'is3D': True,
                'pieSliceText': 'value',
                'legend': {'position': 'labeled', 'maxLines': 3, 'textStyle': {'fontSize': 16,}},
                },
            width=kwargs.get('width', self.width), height=kwargs.get('height', self.height),
            )

    def get_js_template(self):
        return "statistiques/gchart/pie_chart.html"

    def get_html_template(self):
        return "statistiques/gchart/html.html"
