# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20150706_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bugzillabug',
            name='bugzilla_id',
            field=models.IntegerField(unique=True),
        ),
    ]
