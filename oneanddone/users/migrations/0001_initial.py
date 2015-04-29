# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('consent_to_email', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, verbose_name='Display Name:')),
                ('privacy_policy_accepted', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=30, unique=True, null=True, verbose_name='Username')),
                ('personal_url', models.URLField(null=True, blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
