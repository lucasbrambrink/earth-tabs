# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-14 01:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_auto_20180114_0129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='lat',
            field=models.DecimalField(decimal_places=12, max_digits=16, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='long',
            field=models.DecimalField(decimal_places=12, max_digits=16, null=True),
        ),
    ]
