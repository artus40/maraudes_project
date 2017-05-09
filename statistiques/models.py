from django.db import models
from django.shortcuts import reverse
# Create your models here.

NSP = "Ne sait pas"

# Item: Parcours institutionnel
PARCOURS_INSTITUTIONNEL = "Institutionnel"
PARCOURS_FAMILIAL = "Familial"
PARCOURS_DE_VIE_CHOICES = (
    (NSP, "Ne sait pas"),
    (PARCOURS_FAMILIAL, "Parcours familial"),
    (PARCOURS_INSTITUTIONNEL, "Parcours institutionnel"),
    )

#Item: Type d'habitation
HABITATION_SANS = "Sans Abri"
HABITATION_LOGEMENT = "Logement"
HABITATION_TIERS = "Hébergement"
HABITATION_MAL_LOGEMENT = "Mal logé"
HABITATION_CHOICES = (
    (NSP, "Ne sait pas"),
    (HABITATION_SANS, "Sans abri"),
    (HABITATION_TIERS, "Hébergé"),
    (HABITATION_LOGEMENT, "Logé"),
    (HABITATION_MAL_LOGEMENT, "Mal logé"),
    )

#Item: Ressources
RESSOURCES_RSA = "RSA"
RESSOURCES_AAH = "AAH"
RESSOURCES_POLE_EMPLOI = "Pôle Emploi"
RESSOURCES_AUTRES = "Autres"
RESSOURCES_SANS = "Pas de ressources"
RESSOURCES_CHOICES = (
    (NSP, "Ne sait pas"),
    (RESSOURCES_AAH, "AAH"),
    (RESSOURCES_RSA, "RSA"),
    (RESSOURCES_SANS, "Aucune"),
    (RESSOURCES_POLE_EMPLOI, "Pôle emploi"),
    (RESSOURCES_AUTRES, "Autres ressources"),
    )



class FicheStatistique(models.Model):

    sujet = models.OneToOneField('notes.Sujet',
                          on_delete=models.CASCADE,
                          primary_key=True,
                          related_name="statistiques")

    lien_familial = models.NullBooleanField("Lien Familial")
    parcours_de_vie = models.CharField(max_length=64,
                                       choices=PARCOURS_DE_VIE_CHOICES,
                                       default=NSP)

    # Problématiques
    prob_psychiatrie = models.NullBooleanField("Psychiatrie")
    prob_administratif = models.NullBooleanField("Administratif")
    prob_addiction = models.NullBooleanField("Addiction")
    prob_somatique = models.NullBooleanField("Somatique")

    # Logement
    habitation = models.CharField("Type d'habitat", max_length=64,
                                  choices=HABITATION_CHOICES,
                                  default=NSP)
    ressources = models.CharField("Ressources", max_length=64,
                                  choices=RESSOURCES_CHOICES,
                                  default=NSP)
    connu_siao = models.NullBooleanField("Connu du SIAO ?")

    def get_absolute_url(self):
        return reverse('notes:details-sujet', kwargs={'pk': self.sujet.pk})

    @property
    def info_completed(self):
        observed = ('prob_psychiatrie', 'prob_addiction',
                    'prob_administratif', 'prob_somatique', 'habitation', 'ressources',
                    'connu_siao', 'lien_familial', 'parcours_de_vie')
        completed = 0
        for f in observed:
            if getattr(self, f) == None or getattr(self, f) == NSP:
                continue
            else:
                completed += 1
        return int(completed / len(observed) * 100)
