# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-13 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0008_auto_20170213_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='postal_code',
            field=models.CharField(max_length=6),
        ),
    ]
