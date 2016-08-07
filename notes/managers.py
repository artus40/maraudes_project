from django.db.models import Manager
from django.db.models.query import QuerySet


class NoteQuerySet(QuerySet):

    def _ordered_by_field(self, field, reverse=False):
        return self.order_by(   '%s%s' % (  "-" if reverse else "",
                                            field
                                        )
                            )

    def by_date(self, reverse=False):
        return self._ordered_by_field('created_date', reverse=reverse)

    def by_time(self, reverse=False):
        return self._ordered_by_field('created_time', reverse=reverse)

class NoteManager(Manager):

    def get_queryset(self):
        return NoteQuerySet(self.model)

    get_query_set = get_queryset

    def by_date(self, **kwargs):
        return self.get_queryset().by_date(**kwargs)

    def by_time(self, **kwargs):
        return self.get_queryset().by_time(**kwargs)


