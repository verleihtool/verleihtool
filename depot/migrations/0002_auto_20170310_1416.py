# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 14:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='depot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='depot.Depot'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='visibility',
            field=models.CharField(choices=[('1', 'public'), ('2', 'private')], max_length=1),
        ),
    ]