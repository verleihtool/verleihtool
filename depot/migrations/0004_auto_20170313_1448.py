# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0003_depot_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.PositiveSmallIntegerField(),
        ),
    ]