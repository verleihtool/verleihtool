# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-08 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0010_auto_20171006_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='depot',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='depot',
            name='name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]
