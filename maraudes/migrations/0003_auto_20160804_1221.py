# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-04 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import maraudes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('maraudes', '0002_auto_20160804_1221'),
        ('utilisateurs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maraude',
            name='binome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maraudes', to='utilisateurs.Maraudeur', verbose_name='Binôme'),
        ),
        migrations.AddField(
            model_name='maraude',
            name='referent',
            field=models.ForeignKey(default=maraudes.models.get_referent_maraude, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='utilisateurs.Maraudeur', verbose_name='Référent'),
        ),
        migrations.CreateModel(
            name='CompteRendu',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('maraudes.maraude',),
        ),
    ]