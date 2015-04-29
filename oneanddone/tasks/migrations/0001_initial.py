# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BugzillaBug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bugzilla_id', models.IntegerField(unique=True, max_length=20)),
                ('summary', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
                ('time_spent_in_minutes', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99999)])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('difficulty', models.IntegerField(default=1, verbose_name=b'task difficulty', choices=[(1, b'Beginner'), (2, b'Intermediate'), (3, b'Advanced')])),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('execution_time', models.IntegerField(default=30, verbose_name=b'estimated time', choices=[(15, 15), (30, 30), (45, 45), (60, 60)])),
                ('instructions', models.TextField()),
                ('is_draft', models.BooleanField(default=False, verbose_name=b'draft')),
                ('is_invalid', models.BooleanField(default=False, verbose_name=b'invalid')),
                ('name', models.CharField(unique=True, max_length=255, verbose_name=b'title')),
                ('prerequisites', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=3, verbose_name=b'task priority', choices=[(1, b'P1'), (2, b'P2'), (3, b'P3')])),
                ('repeatable', models.BooleanField(default=True)),
                ('short_description', models.CharField(max_length=255, null=True, verbose_name=b'description', blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('why_this_matters', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['priority', 'difficulty'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskAttempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('requires_notification', models.BooleanField(default=False)),
                ('state', models.IntegerField(default=0, choices=[(0, b'Started'), (1, b'Finished'), (2, b'Abandoned'), (3, b'Closed')])),
                ('task', models.ForeignKey(related_name='taskattempt_set', to='tasks.Task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-modified'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskImportBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(help_text=b'\n        A summary of what items are being imported.\n    ', max_length=255, verbose_name=b'batch summary')),
                ('query', models.TextField(help_text=b'\n        The URL to the Bugzilla@Mozilla search query that yields the items you\n        want to create tasks from.\n    ', verbose_name=b'query URL')),
                ('source', models.IntegerField(default=0, choices=[(0, b'Bugzilla@Mozilla'), (1, b'Other')])),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskInvalidationCriterion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('field_name', models.CharField(help_text=b'\n        Name of field recognized by Bugzilla@Mozilla REST API. Examples:\n        status, resolution, component.\n    ', max_length=80)),
                ('field_value', models.CharField(help_text=b'\n        Target value of the field to be checked.\n    ', max_length=80)),
                ('relation', models.IntegerField(default=0, help_text=b'\n        Relationship (equality/inequality) between name and value.\n    ', choices=[(0, b'=='), (1, b'!=')])),
                ('batches', models.ManyToManyField(to='tasks.TaskImportBatch')),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'task invalidation criteria',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskKeyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'keyword')),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('task', models.ForeignKey(related_name='keyword_set', to='tasks.Task')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskMetrics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('abandoned_users', models.IntegerField(null=True, blank=True)),
                ('closed_users', models.IntegerField(null=True, blank=True)),
                ('completed_users', models.IntegerField(null=True, blank=True)),
                ('incomplete_users', models.IntegerField(null=True, blank=True)),
                ('user_completes_then_completes_another_count', models.IntegerField(null=True, blank=True)),
                ('user_completes_then_takes_another_count', models.IntegerField(null=True, blank=True)),
                ('user_takes_then_quits_count', models.IntegerField(null=True, blank=True)),
                ('too_short_completed_attempts_count', models.IntegerField(null=True, blank=True)),
                ('task', models.OneToOneField(to='tasks.Task')),
            ],
            options={
                'ordering': ['-completed_users'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('creator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='task',
            name='batch',
            field=models.ForeignKey(blank=True, to='tasks.TaskImportBatch', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='next_task',
            field=models.ForeignKey(related_name='previous_task', blank=True, to='tasks.Task', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='owner',
            field=models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='project',
            field=models.ForeignKey(blank=True, to='tasks.TaskProject', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='team',
            field=models.ForeignKey(to='tasks.TaskTeam'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='type',
            field=models.ForeignKey(blank=True, to='tasks.TaskType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedback',
            name='attempt',
            field=models.OneToOneField(to='tasks.TaskAttempt'),
            preserve_default=True,
        ),
    ]
