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

      if obj.state == 'PL' or obj.state == 'FN':
        toReturn['time_played'] = PlaylistEntryTimePlayed.objects.get(playlist_entry=obj).time_played.replace(microsecond=0).isoformat()
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
        toReturn['latitude'] = location.point.y
        toReturn['longitude'] = location.point.x

      return toReturn

    return json.JSONEncoder.default(self, obj)


