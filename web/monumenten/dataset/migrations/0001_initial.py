# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-20 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monument',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
    ]
