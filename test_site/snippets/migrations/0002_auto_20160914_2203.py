# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-14 22:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calltoaction',
            name='url',
            field=models.URLField(blank=True, help_text=b'\n    \t\tUse local links for pages on the site, without the root domain. Example: "/shop/". \n    \t\tUse the full URL for pages on subdomains. Example: "https://memberhub.virginmobileusa.com".\n    \t\t', null=True, verbose_name=b'Link URL'),
        ),
    ]
