import json

from udj.decorators import NeedsJSON
from udj.decorators import AcceptsMethods
from udj.decorators import PlayerExists
from udj.authdecorators import NeedsAuth
from udj.authdecorators import TicketUserMatch
from udj.models import LibraryEntry
from udj.models import Player
from udj.headers import MISSING_RESOURCE_HEADER

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist

def isValidLibraryEntryJSON(libraryEntry):
  return "id" in libraryEntry \
    and "title" in libraryEntry \
    and "artist" in libraryEntry \
    and "album" in libraryEntry \
    and "genre" in libraryEntry \
    and "track" in libraryEntry \
    and "duration" in libraryEntry \

@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['PUT'])
@NeedsJSON
@PlayerExists
def addSong2Library(request, user_id, player_id, player):

  try:
    libJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')


  try:
    if LibraryEntry.objects.filter(player=player, player_lib_song_id=libJSON['id']).exists():
      return HttpResponse(status=409)
    LibraryEntry(
      player=player,
      player_lib_song_id=libJSON['id'],
      title=libJSON['title'],
      artist=libJSON['artist'],
      album=libJSON['album'],
      genre=libJSON['genre'],
      track=libJSON['track'],
      duration=libJSON['duration']).save()
  except KeyError:
    return HttpResponseBadRequest('Bad JSON')

  return HttpResponse(status=201)

@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['DELETE'])
@PlayerExists
def deleteSongFromLibrary(request, user_id, player_id, lib_id, player):
  try:
    libEntry = LibraryEntry.objects.get(player=player, player_lib_song_id=lib_id)
    libEntry.is_deleted = True
    libEntry.save()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse()

@NeedsAuth
@TicketUserMatch
@PlayerExists
@AcceptsMethods(['PUT', 'DELETE'])
def modifyBanList(request, user_id, player_id, lib_id, player):
  try:
    libEntry = LibraryEntry.objects.get(player=player, player_lib_song_id=lib_id)
    libEntry.is_banned=True if request.method == 'PUT' else False
    libEntry.save()
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn





"""
import json
from udj.headers import getDjangoUUIDHeader
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from udj.decorators import TicketUserMatch
from udj.decorators import NeedsUUID
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import getLibraryEntryFromJSON
from udj.models import LibraryEntry
from udj.utils import getJSONResponse

def addSongToLibrary(songJson, user_id, uuid):
  preivouslyAdded = LibraryEntry.objects.filter(
    host_lib_song_id=songJson['id'],
    machine_uuid=uuid,
    owning_user__id=user_id)
  if preivouslyAdded.exists():
    return preivouslyAdded[0]
  else:
    toInsert = getLibraryEntryFromJSON(songJson, user_id, uuid)
    toInsert.save()
    return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
@NeedsUUID
def addSongsToLibrary(request, user_id):

  uuid = request.META[getDjangoUUIDHeader()]
  #TODO catch any exception in the json parsing and return a bad request
  songsToAdd = json.loads(request.raw_post_data)

  toReturn = []
  for libEntry in songsToAdd:
    addedSong = addSongToLibrary(libEntry, user_id, uuid)
    toReturn.append(addedSong.host_lib_song_id)

  return getJSONResponse(json.dumps(toReturn), status=201)

@AcceptsMethods('DELETE')
@TicketUserMatch
@NeedsUUID
def deleteSongFromLibrary(request, user_id, lib_id):
  try:
    uuid = request.META[getDjangoUUIDHeader()]
    toDelete = LibraryEntry.objects.get(
      machine_uuid=uuid,
      host_lib_song_id=lib_id,
      owning_user=user_id)
    toDelete.is_deleted = True
    toDelete.save()
  except ObjectDoesNotExist:
    return HttpResponseNotFound()
  return HttpResponse("Deleted item: " + lib_id)
"""
