# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 20:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20170804_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthimage',
            name='source',
            field=models.CharField(choices=[('reddit', 'reddit.com/r/Earth'), ('apod', "NASA's Astronomy Picture of the Day")], default='reddit', max_length=100),
        ),
        migrations.AddField(
            model_name='querysetting',
            name='allowed_sources',
            field=models.CharField(default='reddit', max_length=255),
        ),
    ]
