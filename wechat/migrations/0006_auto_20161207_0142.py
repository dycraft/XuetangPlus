# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-07 01:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0005_auto_20161207_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, default='', max_length=32),
        ),
    ]
