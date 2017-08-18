from django.db.models import (Field, NullBooleanField,
                              Count,
                              )
from graphos.sources.simple import SimpleDataSource
from graphos.renderers import gchart

# Defines generic labels for common fields
LABELS = {
        NullBooleanField: {True: "Oui", False: "Non", None:"Ne sait pas"},
    }

class FieldValuesCountDataSource(SimpleDataSource):
    """ Generates data from a limited set of choices.

    """
    def __init__(self, queryset, field, labels=None, excluded=[]):
        self.queryset = queryset
        self.field_name = field.name
        self.excluded = excluded
        if not labels:
            if field.__class__ in LABELS:
                labels = LABELS[field.__class__]
            elif field.choices:
                labels = dict(field.choices)
            else:
                raise ValueError("Could not retrieve labels for", field)
        self.labels = labels
        super().__init__(self.create_data())

    def create_data(self):
        data = [(self.field_name, "%s_count" % self.field_name)]  # Headers
        data += [
            (self.labels[item[self.field_name]],  # Display a label instead of raw values
             item['count']
             ) for item in self.queryset.values(            # Retrieve all values for field
                                            self.field_name
                                        ).annotate(         # Count occurrences of each value
                                            count=Count('pk')
                                        ).order_by()        # Needed so that counts are aggregated
            # Exclude values that are marked to be ignored
            if (not self.excluded
                or item[self.field_name] not in self.excluded)
        ]
        return data


class PieWrapper(gchart.PieChart):
    """ A wrapper around gchart.PieChart that generates a graph from :

        - a queryset and a model field (NullBooleanField or field with choices)
        OR
        - a data object and title
    """

    height=400
    width=800

    def __init__(self,
                 queryset=None, field=None,
                 data=None, title=None,
                 null_values=[],
                 **kwargs):
        if not data:
            if not isinstance(field, Field):
                raise TypeError(field, 'must be a child of django.models.db.fields.Field !')
            if not queryset:
                raise TypeError("You must give either a queryset and field or data")
            data_source = FieldValuesCountDataSource(
                queryset, field,
                excluded=null_values,
                labels=None  #TODO: How to pass in labels ??
            )
        else:
            data_source = SimpleDataSource(data=data)

        super().__init__(
            data_source,
            options={
                'title': getattr(field, 'verbose_name', title),
                'is3D': True,
                'pieSliceText': 'value',
                'legend': {'position': 'labeled', 'maxLines': 3, 'textStyle': {'fontSize': 16,}},
                },
            width=kwargs.get('width', self.width),
            height=kwargs.get('height', self.height),
            )

    def get_js_template(self):
        return "statistiques/gchart/pie_chart.html"

    def get_html_template(self):
        return "statistiques/gchart/html.html"


class ColumnWrapper(gchart.ColumnChart):

    pass
