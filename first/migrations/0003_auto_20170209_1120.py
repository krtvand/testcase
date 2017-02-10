# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-09 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0002_auto_20170209_1028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='weight',
            name='type',
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
        migrations.DeleteModel(
            name='Currency',
        ),
        migrations.DeleteModel(
            name='Price',
        ),
        migrations.DeleteModel(
            name='Weight',
        ),
        migrations.DeleteModel(
            name='WeightType',
        ),
    ]
