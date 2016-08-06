from django.db.models import Manager

class NoteManager(Manager):

    def by_date(self):
        return self.get_queryset().order_by('created_date')

    def by_time(self):
        return self.get_queryset().order_by('created_time')
