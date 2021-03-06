# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-16 06:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0010_auto_20170215_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='postal_code',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name='barcode',
            name='value',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='barcodetype',
            name='type',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='barcode',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='first.Barcode'),
        ),
    ]
