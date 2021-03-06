# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 23:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20170806_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earthimage',
            name='source',
            field=models.CharField(choices=[('all', 'all'), ('reddit', 'reddit.com/r/Earth'), ('apod', "NASA's Astronomy Picture of the Day"), ('wiki', 'Wikipedia Picture of the Day')], default='reddit', max_length=100),
        ),
        migrations.AlterField(
            model_name='filter',
            name='source',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('reddit', 'reddit.com/r/Earth'), ('apod', "NASA's Astronomy Picture of the Day"), ('wiki', 'Wikipedia Picture of the Day')], default='', max_length=20),
        ),
    ]
