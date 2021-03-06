# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-10 11:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0005_auto_20170210_1353'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isdelivered', models.BooleanField()),
                ('isrefused', models.BooleanField()),
                ('departure_date', models.DateTimeField()),
                ('delivery_date', models.DateTimeField()),
                ('cost_of_delivery', models.DecimalField(decimal_places=2, max_digits=9)),
                ('products', models.ManyToManyField(to='first.Product')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='first.Recipient')),
            ],
        ),
    ]
