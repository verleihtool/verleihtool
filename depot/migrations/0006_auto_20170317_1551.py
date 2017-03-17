# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-17 15:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depot', '0005_auto_20170317_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depot',
            name='manager_groups',
            field=models.ManyToManyField(blank=True, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='depot',
            name='manager_users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
