import json
from udj.models import LibraryEntry
from udj.models import Playlist
from udj.models import PlaylistEntry
from django.contrib.auth.models import User
from datetime import datetime

"""
class LibraryEntryEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, LibraryEntry):
      return { 
        'server_lib_song_id' : obj.server_lib_song_id,
        'host_lib_song_id' : obj.host_lib_song_id,
        'song' : obj.song,
        'artist' : obj.artist,
        'album' : obj.album
      }
    else:
      return json.JSONEncoder.default(self, obj)
"""

def getLibraryEntryFromJSON(songJson, user_id, host_lib_id):
  return LibraryEntry( 
    host_lib_song_id = host_lib_id, 
    song = songJson['song'], 
    artist  = songJson['artist'], 
    album = songJson['album'], 
    owning_user = User.objects.filter(id=user_id)[0]
  )

def getPlaylistFromJSON(playlistJson, user_id, host_id):
  return Playlist( 
    host_playlist_id = host_id, 
    name = playlistJson['name'], 
    date_created  = datetime.fromtimestamp(playlistJson['date_created']),
    owning_user = User.objects.filter(id=user_id)[0]
  )

def getPlaylistEntryFromJSON(song_id, playlist_id, user_id, host_id):
  return PlaylistEntry(
    host_playlist_entry_id=host_id,
    playlist=Playlist.objects.filter(
      server_playlist_id=playlist_id, owning_user__id=user_id)[0],
    song = LibraryEntry.objects.filter(
      server_lib_song_id=song_id, owning_user__id=user_id)[0])
