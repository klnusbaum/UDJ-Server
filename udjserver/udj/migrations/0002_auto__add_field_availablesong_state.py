# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AvailableSong.state'
        db.add_column('udj_availablesong', 'state',
                      self.gf('django.db.models.fields.CharField')(default=u'AC', max_length=3),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'AvailableSong.state'
        db.delete_column('udj_availablesong', 'state')

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
        'udj.activeplaylistentry': {
            'Meta': {'unique_together': "(('adder', 'client_request_id', 'event'),)", 'object_name': 'ActivePlaylistEntry'},
            'adder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'client_request_id': ('django.db.models.fields.IntegerField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'QE'", 'max_length': '2'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.availablesong': {
            'Meta': {'unique_together': "(('song', 'event'),)", 'object_name': 'AvailableSong'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'AC'", 'max_length': '3'})
        },
        'udj.event': {
            'Meta': {'object_name': 'Event'},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'AC'", 'max_length': '2'}),
            'time_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.eventendtime': {
            'Meta': {'object_name': 'EventEndTime'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_ended': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.eventgoer': {
            'Meta': {'unique_together': "(('user', 'event'),)", 'object_name': 'EventGoer'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'IE'", 'max_length': '2'}),
            'time_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.eventlocation': {
            'Meta': {'object_name': 'EventLocation'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {})
        },
        'udj.eventpassword': {
            'Meta': {'object_name': 'EventPassword'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Event']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'udj.libraryentry': {
            'Meta': {'object_name': 'LibraryEntry'},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'host_lib_song_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine_uuid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'owning_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'udj.playlistentrytimeplayed': {
            'Meta': {'object_name': 'PlaylistEntryTimePlayed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.ActivePlaylistEntry']", 'unique': 'True'}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.ticket': {
            'Meta': {'unique_together': "(('user', 'ticket_hash', 'source_ip_addr'),)", 'object_name': 'Ticket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'ticket_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'time_issued': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.vote': {
            'Meta': {'unique_together': "(('user', 'playlist_entry'),)", 'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.ActivePlaylistEntry']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['udj']