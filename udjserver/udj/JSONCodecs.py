import json
from udj.models import LibraryEntry
from udj.models import Event
from django.contrib.auth.models import User
from datetime import datetime

def getLibraryEntryFromJSON(songJson, user_id):
  return LibraryEntry( 
    host_lib_song_id = songJson['id'], 
    song = songJson['song'], 
    artist  = songJson['artist'], 
    album = songJson['album'], 
    owning_user = User.objects.filter(id=user_id)[0]
  )

def getJSONForAvailableSongs(songs):
  toReturn = []
  for song in songs:
    toAdd = { 
      "id" : song.library_entry.host_lib_song_id, 
      "song" : song.library_entry.song, 
      "artist" : song.library_entry.artist, 
      "album" : song.library_entry.album,
    }
    toReturn.append(toAdd)
  return json.dumps(toReturn)
    

def getJSONForEvents(events):
  toReturn = []
  for event in events:
    toAdd = {
      'id' : event.id,
      'name' : event.name, 
      'host_id' : event.host.id,
      'latitude' : float(event.latitude),
      'longitude' : float(event.longitude)
    }
    toReturn.append(toAdd)
  return json.dumps(toReturn)

