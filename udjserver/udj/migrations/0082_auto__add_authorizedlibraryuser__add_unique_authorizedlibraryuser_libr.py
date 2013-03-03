# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AuthorizedLibraryUser'
        db.create_table('udj_authorizedlibraryuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['udj.Library'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('user_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('udj', ['AuthorizedLibraryUser'])

        # Adding unique constraint on 'AuthorizedLibraryUser', fields ['library', 'user', 'user_type']
        db.create_unique('udj_authorizedlibraryuser', ['library_id', 'user_id', 'user_type'])

    def backwards(self, orm):
        # Removing unique constraint on 'AuthorizedLibraryUser', fields ['library', 'user', 'user_type']
        db.delete_unique('udj_authorizedlibraryuser', ['library_id', 'user_id', 'user_type'])

        # Deleting model 'AuthorizedLibraryUser'
        db.delete_table('udj_authorizedlibraryuser')

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
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'QE'", 'max_length': '2'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.associatedlibrary': {
            'Meta': {'unique_together': "(('library', 'player'),)", 'object_name': 'AssociatedLibrary'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Library']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"})
        },
        'udj.authorizedlibraryuser': {
            'Meta': {'unique_together': "(('library', 'user', 'user_type'),)", 'object_name': 'AuthorizedLibraryUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Library']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'udj.bannedlibraryentry': {
            'Meta': {'unique_together': "(('song', 'player'),)", 'object_name': 'BannedLibraryEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"})
        },
        'udj.defaultlibrary': {
            'Meta': {'object_name': 'DefaultLibrary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Library']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'})
        },
        'udj.favorite': {
            'Meta': {'object_name': 'Favorite'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'favorite_song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.library': {
            'Meta': {'object_name': 'Library'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pub_key': ('django.db.models.fields.TextField', [], {}),
            'read_permission': ('django.db.models.fields.CharField', [], {'default': "u'OW'", 'max_length': '2'}),
            'resolver': ('django.db.models.fields.CharField', [], {'default': "'standard'", 'max_length': '200'}),
            'write_permission': ('django.db.models.fields.CharField', [], {'default': "u'OW'", 'max_length': '2'})
        },
        'udj.libraryentry': {
            'Meta': {'object_name': 'LibraryEntry'},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lib_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Library']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        'udj.ownedlibrary': {
            'Meta': {'object_name': 'OwnedLibrary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Library']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.participant': {
            'Meta': {'unique_together': "(('user', 'player'),)", 'object_name': 'Participant'},
            'ban_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kick_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logout_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'time_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_last_interaction': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.player': {
            'Meta': {'unique_together': "(('owning_user', 'name'),)", 'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owning_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'size_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sorting_algo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.SortingAlgorithm']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'IN'", 'max_length': '2'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'udj.playerlocation': {
            'Meta': {'object_name': 'PlayerLocation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'U.S.'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locality': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0.0 0.0)'"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'default': "'00000'", 'max_length': '20'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        'udj.playerpassword': {
            'Meta': {'object_name': 'PlayerPassword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'time_set': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.playerpermission': {
            'Meta': {'object_name': 'PlayerPermission'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.PlayerPermissionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"})
        },
        'udj.playerpermissiongroup': {
            'Meta': {'unique_together': "(('player', 'name'),)", 'object_name': 'PlayerPermissionGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"})
        },
        'udj.playerpermissiongroupmember': {
            'Meta': {'object_name': 'PlayerPermissionGroupMember'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.PlayerPermissionGroup']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.playlistentrytimeplayed': {
            'Meta': {'object_name': 'PlaylistEntryTimePlayed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['udj.ActivePlaylistEntry']", 'unique': 'True'}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.songset': {
            'Meta': {'unique_together': "(('player', 'name'),)", 'object_name': 'SongSet'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"})
        },
        'udj.songsetentry': {
            'Meta': {'object_name': 'SongSetEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'songset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.SongSet']"})
        },
        'udj.sortingalgorithm': {
            'Meta': {'object_name': 'SortingAlgorithm'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'function_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'udj.ticket': {
            'Meta': {'unique_together': "(('user', 'ticket_hash'),)", 'object_name': 'Ticket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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