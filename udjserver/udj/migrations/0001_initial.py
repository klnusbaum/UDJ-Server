# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table('udj_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('time_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'AC', max_length=2)),
        ))
        db.send_create_signal('udj', ['Event'])

        # Adding model 'EventEndTime'
        db.create_table('udj_eventendtime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'], unique=True)),
            ('time_ended', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('udj', ['EventEndTime'])

        # Adding model 'EventPassword'
        db.create_table('udj_eventpassword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'], unique=True)),
            ('password_hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('udj', ['EventPassword'])

        # Adding model 'EventLocation'
        db.create_table('udj_eventlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'], unique=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('udj', ['EventLocation'])

        # Adding model 'LibraryEntry'
        db.create_table('udj_libraryentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host_lib_song_id', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('artist', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('album', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('owning_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('machine_uuid', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('udj', ['LibraryEntry'])

        # Adding model 'AvailableSong'
        db.create_table('udj_availablesong', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.LibraryEntry'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'])),
        ))
        db.send_create_signal('udj', ['AvailableSong'])

        # Adding unique constraint on 'AvailableSong', fields ['song', 'event']
        db.create_unique('udj_availablesong', ['song_id', 'event_id'])

        # Adding model 'ActivePlaylistEntry'
        db.create_table('udj_activeplaylistentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.LibraryEntry'])),
            ('time_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('adder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'])),
            ('client_request_id', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'QE', max_length=2)),
        ))
        db.send_create_signal('udj', ['ActivePlaylistEntry'])

        # Adding unique constraint on 'ActivePlaylistEntry', fields ['adder', 'client_request_id', 'event']
        db.create_unique('udj_activeplaylistentry', ['adder_id', 'client_request_id', 'event_id'])

        # Adding model 'PlaylistEntryTimePlayed'
        db.create_table('udj_playlistentrytimeplayed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('playlist_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.ActivePlaylistEntry'], unique=True)),
            ('time_played', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('udj', ['PlaylistEntryTimePlayed'])

        # Adding model 'Ticket'
        db.create_table('udj_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ticket_hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('source_ip_addr', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('time_issued', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('udj', ['Ticket'])

        # Adding unique constraint on 'Ticket', fields ['user', 'ticket_hash', 'source_ip_addr']
        db.create_unique('udj_ticket', ['user_id', 'ticket_hash', 'source_ip_addr'])

        # Adding model 'EventGoer'
        db.create_table('udj_eventgoer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Event'])),
            ('time_joined', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'IE', max_length=2)),
        ))
        db.send_create_signal('udj', ['EventGoer'])

        # Adding unique constraint on 'EventGoer', fields ['user', 'event']
        db.create_unique('udj_eventgoer', ['user_id', 'event_id'])

        # Adding model 'Vote'
        db.create_table('udj_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('playlist_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.ActivePlaylistEntry'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('weight', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('udj', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['user', 'playlist_entry']
        db.create_unique('udj_vote', ['user_id', 'playlist_entry_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'Vote', fields ['user', 'playlist_entry']
        db.delete_unique('udj_vote', ['user_id', 'playlist_entry_id'])

        # Removing unique constraint on 'EventGoer', fields ['user', 'event']
        db.delete_unique('udj_eventgoer', ['user_id', 'event_id'])

        # Removing unique constraint on 'Ticket', fields ['user', 'ticket_hash', 'source_ip_addr']
        db.delete_unique('udj_ticket', ['user_id', 'ticket_hash', 'source_ip_addr'])

        # Removing unique constraint on 'ActivePlaylistEntry', fields ['adder', 'client_request_id', 'event']
        db.delete_unique('udj_activeplaylistentry', ['adder_id', 'client_request_id', 'event_id'])

        # Removing unique constraint on 'AvailableSong', fields ['song', 'event']
        db.delete_unique('udj_availablesong', ['song_id', 'event_id'])

        # Deleting model 'Event'
        db.delete_table('udj_event')

        # Deleting model 'EventEndTime'
        db.delete_table('udj_eventendtime')

        # Deleting model 'EventPassword'
        db.delete_table('udj_eventpassword')

        # Deleting model 'EventLocation'
        db.delete_table('udj_eventlocation')

        # Deleting model 'LibraryEntry'
        db.delete_table('udj_libraryentry')

        # Deleting model 'AvailableSong'
        db.delete_table('udj_availablesong')

        # Deleting model 'ActivePlaylistEntry'
        db.delete_table('udj_activeplaylistentry')

        # Deleting model 'PlaylistEntryTimePlayed'
        db.delete_table('udj_playlistentrytimeplayed')

        # Deleting model 'Ticket'
        db.delete_table('udj_ticket')

        # Deleting model 'EventGoer'
        db.delete_table('udj_eventgoer')

        # Deleting model 'Vote'
        db.delete_table('udj_vote')

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
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"})
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