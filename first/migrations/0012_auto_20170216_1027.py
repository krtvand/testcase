# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-16 07:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0011_auto_20170216_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcode',
            name='value',
            field=models.CharField(max_length=256),
        ),
    ]
