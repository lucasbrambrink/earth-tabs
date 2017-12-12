# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-12 02:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_querysetting_is_administrator'),
    ]

    operations = [
        migrations.AddField(
            model_name='querysetting',
            name='align',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='querysetting',
            name='allowed_sources',
            field=models.CharField(blank=True, default='reddit', max_length=255),
        ),
        migrations.AlterField(
            model_name='querysetting',
            name='contain_data_sources',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='querysetting',
            name='history',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='querysetting',
            name='relative_frequency',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
