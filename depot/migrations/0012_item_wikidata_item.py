# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-09 08:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0011_auto_20171008_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='wikidata_item',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
