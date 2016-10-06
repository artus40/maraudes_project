from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.db import models

### Item choices

# Item: Parcours institutionnel
PARCOURS_INSTITUTIONNEL = "Institutionnel"
PARCOURS_FAMILIAL = "Familial"
PARCOURS_NR = "Non renseigné"
PARCOURS_DE_VIE_CHOICES = (
    (PARCOURS_FAMILIAL, "Parcours familial"),
    (PARCOURS_INSTITUTIONNEL, "Parcours institutionnel"),
    (PARCOURS_NR, "Ne sait pas"),
    )

#Item: Type d'habitation
HABITATION_SANS = "Sans Abri"
HABITATION_LOGEMENT = "Logement"
HABITATION_TIERS = "Hébergement"
HABITATION_MAL_LOGEMENT = "Mal logé"
HABITATION_NR = "Non renseigné"
HABITATION_CHOICES = (
    (HABITATION_SANS, "Sans abri"),
    (HABITATION_TIERS, "Hébergé"),
    (HABITATION_LOGEMENT, "Logé"),
    (HABITATION_MAL_LOGEMENT, "Mal logé"),
    (HABITATION_NR, "Ne sait pas"),
    )

#Item: Ressources
RESSOURCES_RSA = "RSA"
RESSOURCES_AAH = "AAH"
RESSOURCES_POLE_EMPLOI = "Pôle Emploi"
RESSOURCES_AUTRES = "Autres"
RESSOURCES_SANS = "Pas de ressources"
RESSOURCES_NR = "Non renseigné"
RESSOURCES_CHOICES = (
    (RESSOURCES_AAH, "AAH"),
    (RESSOURCES_RSA, "RSA"),
    (RESSOURCES_SANS, "Aucune"),
    (RESSOURCES_POLE_EMPLOI, "Pôle emploi"),
    (RESSOURCES_AUTRES, "Autres ressources"),
    (RESSOURCES_NR, "Ne sait pas")
    )



### Models
# - Personne
# - Sujet

HOMME = 'M'
FEMME = 'Mme'
GENRE_CHOICES = (
        (HOMME, 'Homme'),
        (FEMME, 'Femme'),
    )

class Personne(models.Model):
    """ Modèle de base d'une personne
        - genre
        - nom
        - prénom
    """

    genre = models.CharField(max_length=3,
                             choices=GENRE_CHOICES,
                             default=HOMME)
    nom = models.CharField(max_length=32, blank=True)
    prenom = models.CharField(max_length=32, blank=True)
    surnom = models.CharField(max_length=64, blank=True)

    def __str__(self):
        string = '%s ' % self.genre
        if self.nom:    string += '%s ' % self.nom
        if self.surnom: string += '"%s" ' % self.surnom
        if self.prenom: string += '%s' % self.prenom
        return string

    def clean(self):
        if not any([self.nom, self.prenom, self.surnom]):
            raise ValidationError(_("Vous devez remplir au moins un nom, prénom ou surnom"))
        return super().clean()

#TODO:
# Il serait préférable de séparer le Sujet (nom, prénom, age)
# des données utilisées pour les statistiques
# Solution : nouveau modèle "Informations" avec OneToOneRelation vers Sujet
# Cette classe pourra être déplacée dans le module 'statistiques'

class Sujet(Personne):
    """ Personne faisant l'objet d'un suivi par la maraude
    """
    # referent = models.ForeignKey("utilisateurs.Professionnel", related_name="suivis")
    premiere_rencontre = models.DateField(
                                    blank=True, null=True,
                                    default=timezone.now
                                    )
    age = models.SmallIntegerField(
                                blank=True, null=True
                                )

    lien_familial = models.NullBooleanField("Lien Familial")
    parcours_de_vie = models.CharField(max_length=64,
                                       choices=PARCOURS_DE_VIE_CHOICES,
                                       default=PARCOURS_NR)

    # Problématiques
    prob_psychiatrie = models.NullBooleanField("Psychiatrie")
    prob_administratif = models.NullBooleanField("Administratif")
    prob_addiction = models.NullBooleanField("Addiction")
    prob_somatique = models.NullBooleanField("Somatique")

    # Logement
    habitation = models.CharField("Type d'habitat", max_length=64,
                                  choices=HABITATION_CHOICES,
                                  default=HABITATION_NR)
    ressources = models.CharField("Ressources", max_length=64,
                                  choices=RESSOURCES_CHOICES,
                                  default=RESSOURCES_NR)
    connu_siao = models.NullBooleanField("Connu du SIAO ?")

    class Meta:
        verbose_name = "Sujet"
        ordering = ('surnom', 'nom', 'prenom')
        permissions = (
            ('view_sujets', "Accès à l'application 'sujets'"),
        )

    def get_absolute_url(self):
        return reverse('suivi:details', kwargs={'pk': self.id})
