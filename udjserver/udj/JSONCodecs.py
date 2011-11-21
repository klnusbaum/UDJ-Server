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

def getJsonForLibraryEntry(lib_entry):
  return { 
    "id" : lib_entry.host_lib_song_id, 
    "song" : lib_entry.song, 
    "artist" : lib_entry.artist, 
    "album" : lib_entry.album,
  }
    

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

