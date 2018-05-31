# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-05-31 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0013_auto_20180404_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.CharField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name='item',
            name='wikidata_item',
            field=models.CharField(blank=True, editable=False, max_length=32),
        ),
    ]
