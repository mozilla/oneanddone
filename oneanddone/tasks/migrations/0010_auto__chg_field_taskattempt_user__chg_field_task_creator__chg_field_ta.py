# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TaskAttempt.user'
        db.alter_column('tasks_taskattempt', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))

        # Changing field 'Task.creator'
        db.alter_column('tasks_task', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskKeyword.creator'
        db.alter_column('tasks_taskkeyword', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskType.creator'
        db.alter_column('tasks_tasktype', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskTeam.creator'
        db.alter_column('tasks_taskteam', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskProject.creator'
        db.alter_column('tasks_taskproject', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

    def backwards(self, orm):

        # Changing field 'TaskAttempt.user'
        db.alter_column('tasks_taskattempt', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'Task.creator'
        db.alter_column('tasks_task', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskKeyword.creator'
        db.alter_column('tasks_taskkeyword', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskType.creator'
        db.alter_column('tasks_tasktype', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskTeam.creator'
        db.alter_column('tasks_taskteam', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskProject.creator'
        db.alter_column('tasks_taskproject', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tasks.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'attempt': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskAttempt']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'execution_time': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prerequisites': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskProject']", 'null': 'True', 'blank': 'True'}),
            'repeatable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTeam']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskType']", 'null': 'True', 'blank': 'True'}),
            'why_this_matters': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'tasks.taskattempt': {
            'Meta': {'ordering': "['-modified']", 'object_name': 'TaskAttempt'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        'tasks.taskkeyword': {
            'Meta': {'object_name': 'TaskKeyword'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keyword_set'", 'to': "orm['tasks.Task']"})
        },
        'tasks.taskproject': {
            'Meta': {'object_name': 'TaskProject'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tasks.taskteam': {
            'Meta': {'object_name': 'TaskTeam'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tasks.tasktype': {
            'Meta': {'object_name': 'TaskType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tasks']