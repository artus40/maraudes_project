from django.db import models

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
    #date_created = models.DateField('Crée le')


    def as_table(self):
        pass

    def get_header(self):
        """ Informations included in headers """
        return ('Note', [])

    def get_date(self):
        raise NotImplementedError

    def header_label(self):
        return self.get_header()[0]

    def header_infos(self):
        return self.get_header()[1]

    @property
    def date(self):
        return self.get_date()
