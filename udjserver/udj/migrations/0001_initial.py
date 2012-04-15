# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'State'
        db.create_table('udj_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('udj', ['State'])

        # Adding model 'Player'
        db.create_table('udj_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owning_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('udj', ['Player'])

        # Adding model 'PlayerPassword'
        db.create_table('udj_playerpassword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Player'], unique=True)),
            ('password_hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('time_set', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('udj', ['PlayerPassword'])

        # Adding model 'PlayerLocation'
        db.create_table('udj_playerlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Player'], unique=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.State'])),
            ('zipcode', self.gf('django.db.models.fields.IntegerField')()),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('udj', ['PlayerLocation'])

        # Adding model 'LibraryEntry'
        db.create_table('udj_libraryentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Player'])),
            ('player_lib_song_id', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('artist', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('album', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('udj', ['LibraryEntry'])

        # Adding model 'ActivePlaylistEntry'
        db.create_table('udj_activeplaylistentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.LibraryEntry'])),
            ('time_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('adder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'QE', max_length=2)),
        ))
        db.send_create_signal('udj', ['ActivePlaylistEntry'])

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
            ('source_port', self.gf('django.db.models.fields.IntegerField')()),
            ('time_issued', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('udj', ['Ticket'])

        # Adding unique constraint on 'Ticket', fields ['user', 'ticket_hash', 'source_ip_addr', 'source_port']
        db.create_unique('udj_ticket', ['user_id', 'ticket_hash', 'source_ip_addr', 'source_port'])

        # Adding model 'Participant'
        db.create_table('udj_participant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Player'])),
            ('time_joined', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_last_interaction', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('udj', ['Participant'])

        # Adding unique constraint on 'Participant', fields ['user', 'player']
        db.create_unique('udj_participant', ['user_id', 'player_id'])

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

        # Removing unique constraint on 'Participant', fields ['user', 'player']
        db.delete_unique('udj_participant', ['user_id', 'player_id'])

        # Removing unique constraint on 'Ticket', fields ['user', 'ticket_hash', 'source_ip_addr', 'source_port']
        db.delete_unique('udj_ticket', ['user_id', 'ticket_hash', 'source_ip_addr', 'source_port'])

        # Deleting model 'State'
        db.delete_table('udj_state')

        # Deleting model 'Player'
        db.delete_table('udj_player')

        # Deleting model 'PlayerPassword'
        db.delete_table('udj_playerpassword')

        # Deleting model 'PlayerLocation'
        db.delete_table('udj_playerlocation')

        # Deleting model 'LibraryEntry'
        db.delete_table('udj_libraryentry')

        # Deleting model 'ActivePlaylistEntry'
        db.delete_table('udj_activeplaylistentry')

        # Deleting model 'PlaylistEntryTimePlayed'
        db.delete_table('udj_playlistentrytimeplayed')

        # Deleting model 'Ticket'
        db.delete_table('udj_ticket')

        # Deleting model 'Participant'
        db.delete_table('udj_participant')

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
            'Meta': {'object_name': 'ActivePlaylistEntry'},
            'adder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'QE'", 'max_length': '2'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.libraryentry': {
            'Meta': {'object_name': 'LibraryEntry'},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'player_lib_song_id': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        'udj.participant': {
            'Meta': {'unique_together': "(('user', 'player'),)", 'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'time_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_last_interaction': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owning_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.playerlocation': {
            'Meta': {'object_name': 'PlayerLocation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.State']"}),
            'zipcode': ('django.db.models.fields.IntegerField', [], {})
        },
        'udj.playerpassword': {
            'Meta': {'object_name': 'PlayerPassword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'time_set': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.playlistentrytimeplayed': {
            'Meta': {'object_name': 'PlaylistEntryTimePlayed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.ActivePlaylistEntry']", 'unique': 'True'}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'udj.ticket': {
            'Meta': {'unique_together': "(('user', 'ticket_hash', 'source_ip_addr', 'source_port'),)", 'object_name': 'Ticket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'source_port': ('django.db.models.fields.IntegerField', [], {}),
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