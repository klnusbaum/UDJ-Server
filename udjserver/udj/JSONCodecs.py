import json
from udj.models import LibraryEntry
from udj.models import Event
from django.contrib.auth.models import User
from datetime import datetime
#from prioritycalc import getPriority

def getLibraryEntryFromJSON(songJson, user_id):
  return LibraryEntry( 
    host_lib_song_id = songJson['id'], 
    song = songJson['song'], 
    artist  = songJson['artist'], 
    album = songJson['album'], 
    duration = songJson['duration'],
    owning_user = User.objects.get(id=user_id)
  )

def getJSONForAvailableSongs(songs):
  toReturn = []
  for song in songs:
    toAdd = { 
      'id' : song.library_entry.host_lib_song_id, 
      'song' : song.library_entry.song, 
      'artist' : song.library_entry.artist, 
      'album' : song.library_entry.album,
      'duration' : song.library_entry.duration
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

def getJSONForCurrentSong(currentSong):
  toReturn = {
    'lib_song_id' : currentSong.song.host_lib_song_id,
    'song' : currentSong.song.song,
    'artist' : currentSong.song.artist,
    'album' : currentSong.song.album,
    'duration' : currentSong.song.duration,
    'up_votes' : currentSong.upvotes,
    'down_votes' : currentSong.downvotes,
    'time_added' : currentSong.time_added.isoformat(),
    'time_played' : currentSong.time_played.isoformat(),
    'adder_id' : currentSong.adder.id
  }
  return json.dumps(toReturn)

def getJSONForActivePlaylistEntries(entries):
  toReturn = []
  for entry in entries:
    toReturn.append({
      'lib_song_id' : entry.song.host_lib_song_id,
      'song' : entry.song.song,
      'artist' : entry.song.artist,
      'album' : entry.song.album,
      'duration' : entry.song.duration,
      'up_votes' : entry.upvotes,
      'down_votes' : entry.downvotes,
      'time_added' : entry.time_added.isoformat(),
      'adder_id' : entry.adder.id
    })
  return json.dumps(toReturn)
  


  
  return json.dumps(toReturn) 
