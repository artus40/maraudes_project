from django.db import models
from django.utils.html import format_html

class Note(models.Model):
    """ Note relative à un sujet.
    """

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

    def as_table(self):
        html = format_html(
"<tr><th>{} <span class='label label-info'>{}</span>\
<span class='label label-info'>{}</span></th>\
\n<tr><td>{}</td></tr>",
                            self.sujet,
                            self.created_date,
                            self.created_by,
                            self.text
                           )
        return html

    def as_inline_table(self):
        html = format_html(
"<tr><th class='bg-success'><strong>{}</strong> <small>{}</small> \n\
<span class='label label-info pull-right'>{}</span></th>\n\
<tr><td>{}</td></tr>",
                self.subclass.__qualname__,
                self.created_date,
                self.created_by,
                self.text
                )
        return html

    def _get_child_and_subclass(self):
        self._child_instance = None
        self._subclass = None
        for f in self._meta.get_fields():
            if f.is_relation and f.one_to_one:
                self._child_instance = getattr(self, f.name)
                self._subclass = self._child_instance.__class__
                return

    @property
    def subclass(self):
        if not hasattr(self, '_subclass'):
            self._get_child_and_subclass()
        return self._subclass

    def cast(self):
        if not hasattr(self, '_child_instance'):
            self._get_child_and_subclass()
        return self._child_instance

    def __str__(self):
        return "%s of %s" % (self.subclass.__qualname__, self.created_by)
