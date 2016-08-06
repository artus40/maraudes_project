from django.db import models
from django.utils.html import format_html

from . import managers

class Note(models.Model):
    """ Note relative à un sujet.

        Peut être utilisée comme classe parente.
        Il faut alors définir les méthodes :
        - get_date
        - get_labels
        - get_bg_color
        Les valeurs retournée sont utilisée par les templatetages 'notes'

    """

    objects = managers.NoteManager()

    sujet = models.ForeignKey(
                        'sujets.Sujet',
                        related_name="notes",
                        on_delete=models.CASCADE
                        )
    text = models.TextField()
    created_by = models.ForeignKey(
                        'utilisateurs.Professionnel',
                        blank=True,
                        null=True
                        )
    created_date = models.DateField('Crée le', blank=True, null=True)
    created_time = models.TimeField('Heure', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.created_date or not self.created_time:
            child_instance = self.cast()
            self.created_date = child_instance.note_date()
            self.created_time = child_instance.note_time()
        return super().save(*args, **kwargs)

    def _get_child_class_and_instance(self):
        self._child_instance = self
        self._child_class = self.__class__
        if self._meta.get_parent_list(): # If self is actually child instance
            return
        for f in self._meta.get_fields():
            if f.is_relation and f.one_to_one:
                self._child_instance = getattr(self, f.name)
                self._child_class = self._child_instance.__class__
                return

    @property
    def child_class(self):
        if not hasattr(self, '_child_class'):
            self._get_child_class_and_instance()
        return self._child_class

    def cast(self):
        if not hasattr(self, '_child_instance'):
            self._get_child_class_and_instance()
        return self._child_instance

    def __str__(self):
        return "%s of %s" % (self.child_class.__qualname__, self.created_by)

    ## Attributes used by 'notes' template tags
    # bg_color : background color of header
    # labels : list of strings to put in labels
    def cached_attr(name):
        """ Cached property set on return value of 'get_ATTR' method on
            child instance.
        """
        private_name = '_%s' % name
        def getter(self):
            if not hasattr(self, private_name):
                setattr(self,
                        private_name,
                        # Call *child instance* method
                        getattr(self.cast(), 'note_%s' % name)()
                        )
            return getattr(self, private_name)
        return getter

    bg_colors = property(    cached_attr('bg_colors'),
                            doc="background color of header")
    labels = property(      cached_attr('labels'),
                            doc="list of string to display as labels")
