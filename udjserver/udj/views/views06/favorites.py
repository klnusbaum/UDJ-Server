import json

from udj.models import Player
from udj.models import LibraryEntry
from udj.models import Favorite
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.auth import getUserForTicket
from udj.headers import MISSING_RESOURCE_HEADER
from udj.views.views06.helpers import HttpJSONResponse

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT','DELETE'])
def favorite(request, player_id, lib_id):
  user = getUserForTicket(request)
  if request.method == 'PUT':
    return addSongToFavorite(user, player_id, lib_id)
  elif request.method == 'DELETE':
    return removeSongFromFavorite(user, player_id, lib_id)
  else:
    #Should never get here because of AcceptsMethods decerator
    return HttpResponse(status=405)

def addSongToFavorite(user, player_id, lib_id):
  try:
    player = Player.objects.get(pk=player_id)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'player'
    return toReturn

  try:
    song = LibraryEntry.objects.get(player=player, player_lib_song_id=lib_id)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  addedSong , created = Favorite.objects.get_or_create(user=user,favorite_song=song)
  return HttpResponse(status=201)

def removeSongFromFavorite(user, player_id, lib_id):
  try:
    toDelete = Favorite.objects.get(user=user, favorite_song__player__id=player_id,
        favorite_song__player_lib_song_id=lib_id)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  toDelete.delete()
  return HttpResponse()


@NeedsAuth
@AcceptsMethods(['GET'])
def getFavorites(request, player_id):
  user = getUserForTicket(request)
  favorites = Favorite.objects.filter(user=user, favorite_song__player__id=player_id)
  return HttpJSONResponse(json.dumps(favorites, cls=UDJEncoder))

