# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-14 21:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CallToAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('text', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, null=True, verbose_name=b'Link URL')),
                ('link_text', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
