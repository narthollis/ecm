# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'POSNotification.types'
        db.delete_column(u'pos_posnotification', 'types')

        # Adding field 'POSNotification.type'
        db.add_column(u'pos_posnotification', 'type',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=1, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'POSNotification.types'
        db.add_column(u'pos_posnotification', 'types',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=1, db_index=True),
                      keep_default=False)

        # Deleting field 'POSNotification.type'
        db.delete_column(u'pos_posnotification', 'type')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pos.fuellevel': {
            'Meta': {'ordering': "['pos', 'date', 'type_id']", 'object_name': 'FuelLevel'},
            'consumption': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fuel_levels'", 'to': u"orm['pos.POS']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'type_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        u'pos.pos': {
            'Meta': {'object_name': 'POS'},
            'allow_alliance_members': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_corporation_members': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attack_on_aggression': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attack_on_concord_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attack_on_corp_war': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'authorized_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'visible_group'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'cached_until': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'deploy_flags': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'fuel_type_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'has_sov': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'location_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'moon': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'moon_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'online_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'operators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'operated_poses'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'security_status_threshold': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'standings_threshold': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'state_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'usage_flags': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'use_standings_from': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        u'pos.posnotification': {
            'Meta': {'unique_together': "(('pos', 'internal_ident', 'to'),)", 'object_name': 'POSNotification'},
            'dismissed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'foreign_iden': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_ident': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pos.POS']"}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['pos']