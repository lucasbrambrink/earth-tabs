# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-03 00:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20170802_0012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='earthimage',
            name='base64_encoded_image',
        ),
        migrations.AddField(
            model_name='earthimage',
            name='preferred_image_url',
            field=models.CharField(default='', max_length=255),
        ),
    ]
