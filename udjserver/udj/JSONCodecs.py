import json
from udj.models import LibraryEntry
from django.contrib.auth.models import User

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

def getLibraryEntryFromJSON(songJson, user_id, host_lib_id):
  return LibraryEntry( 
    host_lib_song_id = host_lib_id, 
    song = songJson['song'], 
    artist  = songJson['artist'], 
    album = songJson['album'], 
    owning_user = User.objects.filter(id=user_id)[0]
  )
