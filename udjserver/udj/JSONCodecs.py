import json
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import PlaylistEntryTimePlayed
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.contrib.auth.models import User


class UDJEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, QuerySet):
      return [x for x in obj]

    elif isinstance(obj, PlaylistEntryTimePlayed):
      toReturn = self.default(obj.playlist_entry)
      toReturn['time_played'] = obj.time_played.replace(microsecond=0).isoformat()
      return toReturn

    elif isinstance(obj, User):
      return {
        'id' : obj.id,
        'username' : obj.username,
        'first_name' : obj.first_name,
        'last_name' : obj.last_name
      }
    elif isinstance(obj, ActivePlaylistEntry):
      toReturn =  {
        'song' : obj.song,
        'upvoters' : obj.upvoters(),
        'downvoters' : obj.downvoters(),
        'time_added' : obj.time_added.replace(microsecond=0).isoformat(),
        'adder' : obj.adder
      }

      if obj.state == 'PL':
        toReturn['time_player'] = PlaylistEntryTimePlayed.objects.get(playlist_entry=obj).time_played.replace(microsecond=0).isoformat()
      return toReturn



    elif isinstance(obj, LibraryEntry):
      return {
          'id' : obj.player_lib_song_id,
          'title' : obj.title,
          'artist' : obj.artist,
          'album' : obj.album,
          'track' : obj.track,
          'genre' : obj.genre,
          'duration' : obj.duration
      }

    elif isinstance(obj, Participant):
      return {
          'username' : obj.user.username,
          'first_name' : obj.user.first_name,
          'last_name' : obj.user.last_name
      }
    elif isinstance(obj, Player):
      location = None
      try:
        location = PlayerLocation.objects.get(player=obj)
      except ObjectDoesNotExist:
        pass

      toReturn = {
        "id" : obj.id,
        "name" : obj.name,
        "owner_username" : obj.owning_user.username,
        "owner_id" : obj.owning_user.id,
        "has_password" : True if PlayerPassword.objects.filter(player=obj).exists() else False
      }

      if location != None:
        toReturn['latitude'] = location.latitude
        toReturn['longitude'] = location.longitude

      return toReturn

    return json.JSONEncoder.default(self, obj)


"""
import json
from udj.models import LibraryEntry
from udj.models import Event
from udj.models import EventLocation
from udj.models import EventPassword
from udj.models import EventGoer
from django.contrib.auth.models import User
from datetime import datetime
import math

def getLibraryEntryFromJSON(songJson, user_id, uuid):
  return LibraryEntry(
    host_lib_song_id = songJson['id'],
    title = songJson['title'],
    artist  = songJson['artist'],
    album = songJson['album'],
    duration = songJson['duration'],
    owning_user = User.objects.get(id=user_id),
    machine_uuid=uuid
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
  hasPassword = EventPassword.objects.filter(event=event).exists()
  toReturn =  {
    'id' : event.id,
    'name' : event.name, 
    'host_id' : event.host.id,
    'host_username' : event.host.username,
    'has_password' : hasPassword
  }
  location = EventLocation.objects.filter(event=event)
  if location.exists():
    toReturn['latitude'] = location[0].latitude
    toReturn['longitude'] = location[0].longitude
  return toReturn


def getJSONForEvents(events):
  toReturn = []
  for event in events:
    toReturn.append(getEventDictionary(event))
  return json.dumps(toReturn)

def getActivePlaylistEntryDictionary(entry):
   return { 
      'id' : entry.id,
      'lib_song_id' : entry.song.host_lib_song_id,
      'title' : entry.song.title,
      'artist' : entry.song.artist,
      'album' : entry.song.album,
      'duration' : entry.song.duration,
      'up_votes' : entry.upvote_count(),
      'down_votes' : entry.downvote_count(),
      'time_added' : entry.time_added.replace(microsecond=0).isoformat(),
      'adder_id' : entry.adder.id,
      'adder_username' : entry.adder.username
    }

def getActivePlaylistArray(entries):
  toReturn = []
  for entry in entries:
    toReturn.append(getActivePlaylistEntryDictionary(entry))
  return toReturn

def getEventGoerJSON(eventGoer):
  return {
    'id' : eventGoer.user.id,
    'username' : eventGoer.user.username,
    'first_name' : eventGoer.user.first_name,
    'last_name' : eventGoer.user.last_name,
    'logged_in' : True if eventGoer.state == u'IE' else False
  }

def getJSONForEventGoers(eventGoers):
  toReturn = []
  for eventGoer in eventGoers:
    toReturn.append(getEventGoerJSON(eventGoer))
  return json.dumps(toReturn)

def getDistanceToLocation(eventLocation, lat2, lon2 ):
  lat1 = eventLocation.latitude
  lon1 = eventLocation.longitude
  radius = 6371 # km
  dlat = math.radians(lat2-lat1)
  dlon = math.radians(lon2-lon1)
  a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
      * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = radius * c
  return d


def getJSONForEventsByLocation(latitude, longitude, eventLocations):
  toReturn = []
  lat2 = float(latitude)
  lon2 = float(longitude)
  for eventLocation in eventLocations:
    distance = getDistanceToLocation(eventLocation, lat2, lon2)
    if distance < 5:
      toReturn.append(getEventDictionary(eventLocation.event))
  return json.dumps(toReturn)
"""


