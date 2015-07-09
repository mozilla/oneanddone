# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0002_auto_20150508_1008'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskAttemptCommunication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('type', models.IntegerField(choices=[(0, b'User'), (1, b'Admin')])),
                ('attempt', models.ForeignKey(related_name='communication_set', to='tasks.TaskAttempt')),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='task',
            name='must_be_verified',
            field=models.BooleanField(default=False, verbose_name=b'must be verified'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='verification_instructions',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='taskteam',
            name='url_code',
            field=models.CharField(max_length=30, unique=True, null=True, verbose_name=b'team url suffix'),
            preserve_default=True,
        ),
    ]
