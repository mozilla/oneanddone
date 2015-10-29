# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_bugzilla_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bugzilla_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
