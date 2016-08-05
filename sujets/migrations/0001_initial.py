# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-04 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personne',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.CharField(choices=[('M', 'Homme'), ('Mme', 'Femme')], default='M', max_length=3)),
                ('nom', models.CharField(blank=True, max_length=32)),
                ('prenom', models.CharField(blank=True, max_length=32)),
                ('surnom', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Sujet',
            fields=[
                ('personne_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sujets.Personne')),
                ('premiere_rencontre', models.DateField(default=django.utils.timezone.now)),
                ('age', models.SmallIntegerField(blank=True, null=True)),
                ('lien_familial', models.NullBooleanField(verbose_name='Lien Familial')),
                ('parcours_de_vie', models.CharField(choices=[('Familial', 'Parcours familial'), ('Institutionnel', 'Parcours institutionnel'), ('Non renseigné', 'Ne sait pas')], default='Non renseigné', max_length=64)),
                ('prob_psychiatrie', models.NullBooleanField(verbose_name='Psychiatrie')),
                ('prob_administratif', models.NullBooleanField(verbose_name='Administratif')),
                ('prob_addiction', models.NullBooleanField(verbose_name='Addiction')),
                ('prob_somatique', models.NullBooleanField(verbose_name='Somatique')),
                ('habitation', models.CharField(choices=[('Sans Abri', 'Sans abri'), ('Hébergement', 'Hébergé'), ('Logement', 'Logé'), ('Mal logé', 'Mal logé'), ('Non renseigné', 'Ne sait pas')], default='Non renseigné', max_length=64, verbose_name="Type d'habitat")),
                ('ressources', models.CharField(choices=[('AAH', 'AAH'), ('RSA', 'RSA'), ('Pas de ressources', 'Aucune'), ('Pôle Emploi', 'Pôle emploi'), ('Autres', 'Autres ressources'), ('Non renseigné', 'Ne sait pas')], default='Non renseigné', max_length=64, verbose_name='Ressources')),
                ('connu_siao', models.NullBooleanField(verbose_name='Connu du SIAO ?')),
            ],
            bases=('sujets.personne',),
        ),
    ]