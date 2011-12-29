import json
from udj.models import LibraryEntry
from udj.models import Event
from udj.models import EventGoer
from django.contrib.auth.models import User
from datetime import datetime

def getLibraryEntryFromJSON(songJson, user_id):
  return LibraryEntry( 
    host_lib_song_id = songJson['id'], 
    title = songJson['title'], 
    artist  = songJson['artist'], 
    album = songJson['album'], 
    duration = songJson['duration'],
    owning_user = User.objects.get(id=user_id)
  )

def getJSONForAvailableSongs(songs):
  toReturn = []
  for available_song in songs:
    toAdd = { 
      'id' : available_song.song.host_lib_song_id, 
      'title' : available_song.song.title, 
      'artist' : available_song.song.artist, 
      'album' : available_song.song.album,
      'duration' : available_song.song.duration
    }
    toReturn.append(toAdd)
  return json.dumps(toReturn)
    
def getEventDictionary(event):
  hasPassword = event.password_hash != None
  return {
    'id' : event.id,
    'name' : event.name, 
    'host_id' : event.host.id,
    'host_username' : event.host.username,
    'latitude' : float(event.latitude),
    'longitude' : float(event.longitude),
    'has_password' : hasPassword
  }


def getJSONForEvents(events):
  toReturn = []
  for event in events:
    toReturn.append(getEventDictionary(event))
  return json.dumps(toReturn)

def getActivePlaylistEntryDictionary(entry, upvotes, downvotes):
   return { 
      'id' : entry.id,
      'lib_song_id' : entry.song.host_lib_song_id,
      'title' : entry.song.title,
      'artist' : entry.song.artist,
      'album' : entry.song.album,
      'duration' : entry.song.duration,
      'up_votes' : upvotes,
      'down_votes' : downvotes,
      'time_added' : entry.time_added.replace(microsecond=0).isoformat(),
      'adder_id' : entry.adder.id,
      'adder_username' : entry.adder.username
    }

def getActivePlaylistArray(entries):
  toReturn = []
  for entry in entries:
    toReturn.append(
      getActivePlaylistEntryDictionary(entry, entry.upvotes, entry.downvotes))
  return toReturn

def getEventGoerJSON(eventGoer):
  return {
    'id' : eventGoer.user.id,
    'username' : eventGoer.user.username,
    'first_name' : eventGoer.user.first_name,
    'last_name' : eventGoer.user.last_name
  }

def getJSONForEventGoers(eventGoers):
  toReturn = []
  for eventGoer in eventGoers:
    toReturn.append(getEventGoerJSON(eventGoer))
  return json.dumps(toReturn)

