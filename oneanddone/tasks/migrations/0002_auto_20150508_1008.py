# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskteam',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taskteam',
            name='url_code',
            field=models.CharField(max_length=30, unique=True, null=True),
            preserve_default=True,
        ),
    ]
