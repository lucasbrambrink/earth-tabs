# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-06 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20170805_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='querysetting',
            name='query_keywords_title',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='resolution_threshold',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='resolution_threshold_operand',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='resolution_type',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='score_threshold',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='score_threshold_operand',
        ),
        migrations.RemoveField(
            model_name='querysetting',
            name='score_type',
        ),
        migrations.AlterField(
            model_name='earthimage',
            name='source',
            field=models.CharField(choices=[('all', 'all'), ('reddit', 'reddit.com/r/Earth'), ('apod', "NASA's Astronomy Picture of the Day")], default='reddit', max_length=100),
        ),
        migrations.AlterField(
            model_name='filter',
            name='source',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('reddit', 'reddit.com/r/Earth'), ('apod', "NASA's Astronomy Picture of the Day")], default='', max_length=20),
        ),
    ]
