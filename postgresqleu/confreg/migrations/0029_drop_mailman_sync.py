# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-09 14:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confreg', '0028_conferencenews'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conference',
            name='listadminpwd',
        ),
        migrations.RemoveField(
            model_name='conference',
            name='listadminurl',
        ),
        migrations.RemoveField(
            model_name='conference',
            name='speakerlistadminpwd',
        ),
        migrations.RemoveField(
            model_name='conference',
            name='speakerlistadminurl',
        ),
    ]
