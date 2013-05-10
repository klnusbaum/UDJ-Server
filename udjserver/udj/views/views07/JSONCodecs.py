import json
from udj.models import SortingAlgorithm
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import SongSet
from udj.models import SongSetEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.models import Library
from udj.models import Participant
from udj.models import PlayerPermissionGroup
from udj.models import Favorite
from udj.models import LibraryEntry

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

class UDJEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, QuerySet):
      return [x for x in obj]
    elif isinstance(obj, SortingAlgorithm):
      return {
        'id' : str(obj.id),
        'name' : obj.name,
        'description' : obj.description,
        'uses_adder' : obj.uses_adder,
        'uses_time_added' : obj.uses_time_added,
        'uses_upvotes' : obj.uses_upvotes,
        'uses_downvotes' : obj.uses_downvotes,
        'uses_duration' : obj.uses_duration
      }
    elif isinstance(obj, Player):
      toReturn = {
        "id" : str(obj.id),
        "name" : obj.name,
        "owner" : obj.owning_user,
        "has_password" : True if PlayerPassword.objects.filter(player=obj).exists() else False,
        "sorting_algo": obj.sorting_algo,
        "num_active_users" : len(obj.ActiveParticipants),
        "size_limit" : obj.size_limit if obj.size_limit != None else 0,
        "state" : obj.get_state_display(),
        "volume" : obj.volume
      }

      try:
        toReturn['location'] = PlayerLocation.objects.get(player=obj)
      except ObjectDoesNotExist:
        pass

      return toReturn
    elif isinstance(obj, PlayerLocation):
      return {
          "address" : obj.address if obj.address != None else "",
          "locality" : obj.locality if obj.locality != None else "",
          "region" : obj.region if obj.region != None else "",
          "country" : obj.country,
          "postal_code" : obj.postal_code,
          "latitude" : obj.point.y,
          "longitude" : obj.point.x
      }
    elif isinstance(obj, User):
      return {
        'id' : str(obj.id),
        'username' : obj.username,
        'first_name' : obj.first_name,
        'last_name' : obj.last_name
      }
    elif isinstance(obj, Library):
      return {
        'id' : str(obj.id),
        'name' : obj.name,
        'description' : obj.description,
        'pub_key' : obj.pub_key,
        'read_permission' : obj.get_read_permission_display(),
        'write_permission' : obj.get_write_permission_display()
      }
    elif isinstance(obj, PlayerPermissionGroup):
      return {
        'name' : obj.name,
        'users' : obj.Members
      }
    elif isinstance(obj, Participant):
      return obj.user
    elif isinstance(obj, SongSet):
      return {
          "name" : obj.name,
          "description" : obj.description,
          "songs" : obj.Songs,
          "owner" : obj.owner,
          "date_created" : obj.date_created.replace(microsecond=0).isoformat()
      }
    elif isinstance(obj, SongSetEntry):
      return obj.song
    elif isinstance(obj, ActivePlaylistEntry):
      toReturn =  {
        'song' : obj.song,
        'upvoters' : obj.Upvoters,
        'downvoters' : obj.Downvoters,
        'time_added' : obj.time_added.replace(microsecond=0).isoformat(),
        'adder' : obj.adder
      }

      return toReturn

    elif isinstance(obj, PlaylistEntryTimePlayed):
      toReturn = self.default(obj.playlist_entry)
      toReturn['time_played'] = obj.time_played .replace(microsecond=0) .isoformat()
      return toReturn

    elif isinstance(obj, Favorite):
      return obj.favorite_song

    elif isinstance(obj, LibraryEntry):
      return {
          'id' : str(obj.lib_id),
          'library_id' : str(obj.library.id),
          'title' : obj.title,
          'artist' : obj.artist,
          'album' : obj.album,
          'track' : obj.track,
          'genre' : obj.genre,
          'duration' : obj.duration
      }
    else:
      return json.JSONEncoder.default(self, obj)




