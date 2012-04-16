import json
from django.http import HttpRequest
from django.http import HttpResponse
from udj.decorators import NeedsJSON
from udj.decorators import AcceptsMethods
from udj.decorators import PlayerExists
from udj.authdecorators import NeedsAuth
from udj.authdecorators import TicketUserMatch

def isValidLibraryEntryJSON(libraryEntry):
  return "id" in libraryEntry \
    and "title" in libraryEntry \
    and "artist" in libraryEntry \
    and "album" in libraryEntry \
    and "genre" in libraryEntry \
    and "track_number" in libraryEntry \
    and "duration" in libraryEntry \

@NeedsAuth
@AcceptsMethods(['PUT'])
@TicketUserMatch
@PlayerExists
@NeedsJSON
def addSong2Library(request, user_id, player_id, player):

  try:
    libJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')


  try:
    if LibraryEntry.objets.filter(player=player, player_lib_song_id=libJSON['id']).exists():
      return HttpResponse(status=409)
    LibraryEntry(
      player=player,
      player_lib_song_id=libJSON['id'],
      title=libJSON['title'],
      artist=libJSON['artist'],
      album=libJSON['album'],
      genre=libJSON['genre'],
      track_number=libJSON['track_number'],
      duration=libJSON['duration']).save()
  except KeyError:
    return HttpResponseBadRequest('Bad JSON')

  return HttpResponse(status=201)






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
