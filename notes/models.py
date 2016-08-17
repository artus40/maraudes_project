from django.utils import timezone
from django.utils.html import format_html

from django.db import models
from . import managers

class Note(models.Model):
    """ Note relative à un sujet.

        Peut être utilisée comme classe parente.
        class ChildNote(Note):
            def note_date(self): value for 'create_date'
            def note_time(self): value for 'created_time'
            def note_bg_colors(self): ('header bkgd', 'labels bkgd')
            def note_labels(self): list of objects printed as bootstrap labels

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
    created_date = models.DateField('Date')
    created_time = models.TimeField('Heure')

    def save(self, *args, **kwargs):
        if not self.created_date or not self.created_time:
            child_instance = self.cast()
            self.created_date = child_instance.note_date()
            self.created_time = child_instance.note_time()
        if not self.created_by:
            self.created_by = self.cast().note_author()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.child_class.__qualname__)

    def note_author(self):
        return None

    def note_date(self):
        """ Default 'created_date' value. Child may override this method. """
        return timezone.now().date()

    def note_time(self):
        """ Default 'created_time' value. Child may override this method. """
        return timezone.now().time()

    def note_bg_colors(self):
        """ Returns (header background color, labels color).
            Values must be valid bootstrap color name
        """
        return ("default", "info")

    def note_labels(self):
        """ Returns list of objects that are printed as bootstrap labels """
        return [self.created_by]

    def _get_child_class_and_instance(self):
        """ Get child class and instance of Note, stored in _child_instance
            and _child_class.
            Store self and self.__class__ if self is either a child of Note,
            or a Note instance with no child.
        """
        self._child_instance = self
        self._child_class = self.__class__
        if self._meta.get_parent_list(): # If self is actually child instance
            return
        for f in self._meta.get_fields():
            if f.is_relation and f.one_to_one:
                if hasattr(self, f.name):
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

    ## Attributes used by 'notes' template tags
    # bg_color : background color of header
    # labels : list of strings to put in labels
    def cached_attr(name):
        """ Cached property set on return value of 'note_ATTR' method on
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
    bg_colors = property(cached_attr('bg_colors'), doc="background color of header")
    labels = property(cached_attr('labels'), doc="list of string to display as labels")
