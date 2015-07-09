# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20150527_1054'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskattemptcommunication',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='task',
            name='verification_instructions',
            field=models.TextField(verbose_name=b'How to verify', blank=True),
            preserve_default=True,
        ),
    ]
