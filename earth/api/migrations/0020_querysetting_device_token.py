# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-16 03:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_querysetting_contain_data_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='querysetting',
            name='device_token',
            field=models.CharField(default='', max_length=255),
        ),
    ]