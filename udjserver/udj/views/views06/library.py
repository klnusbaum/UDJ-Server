import json

from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import PlayerExists
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.authdecorators import IsOwnerOrAdmin
from udj.models import LibraryEntry, Player, ActivePlaylistEntry
from udj.headers import MISSING_RESOURCE_HEADER
from udj.views.views06.helpers import HttpJSONResponse, removeIfOnPlaylist, getNonExistantLibIds

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import logging

logger = logging.getLogger("udj.libraryerrors")

def getDuplicateDifferentIds(songs, player):
  badIds = []
  duplicates = []
  for song in songs:
    potentialDuplicate = LibraryEntry.objects.filter(player=player, player_lib_song_id=song['id'], is_deleted=False)
    if potentialDuplicate.exists():
      duplicates.append(song['id']) 
      if (potentialDuplicate[0].title != song['title'] or
      potentialDuplicate[0].artist != song['artist'] or
      potentialDuplicate[0].album != song['album'] or
      potentialDuplicate[0].track != song['track'] or
      potentialDuplicate[0].genre != song['genre'] or
      potentialDuplicate[0].duration != song['duration']):
        badIds.append(song['id'])
  return (duplicates, badIds)




def addSongs(libJSON, player):
  for libEntry in libJSON:
    LibraryEntry(
      player=player,
      player_lib_song_id=libEntry['id'],
      title=libEntry['title'],
      artist=libEntry['artist'],
      album=libEntry['album'],
      genre=libEntry['genre'],
      track=libEntry['track'],
      duration=libEntry['duration']).save()

def deleteSongs(songIds, player):
  for song_id in songIds:
    libEntry = LibraryEntry.objects.get(player=player, player_lib_song_id=song_id)
    libEntry.is_deleted = True
    libEntry.save()
    removeIfOnPlaylist(libEntry)



@csrf_exempt
@transaction.commit_on_success
@NeedsAuth
@AcceptsMethods(['PUT'])
@PlayerExists
@IsOwnerOrAdmin
@NeedsJSON
def addSongs2Library(request, player_id, player):

  try:
    libJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  try:
    duplicates, badIds = getDuplicateDifferentIds(libJSON, player)
    if len(badIds) > 0:
      return HttpJSONResponse(json.dumps(badIds), status=409)
    else:
      addSongs(filter(lambda song: song['id'] not in duplicates, libJSON), player)
  except KeyError as e:
    return HttpResponseBadRequest("Bad JSON. Missing key: " + str(e))
  except ValueError as f:
    return HttpResponseBadRequest("Bad JSON. Bad value: " + str(f))

  return HttpResponse(status=201)

@csrf_exempt
@transaction.commit_on_success
@NeedsAuth
@AcceptsMethods(['DELETE'])
@PlayerExists
@IsOwnerOrAdmin
def deleteSongFromLibrary(request, player_id, lib_id, player):

  try:
    deleteSongs([lib_id], player)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse()

@csrf_exempt
@transaction.commit_on_success
@NeedsAuth
@AcceptsMethods(['POST'])
@PlayerExists
@IsOwnerOrAdmin
@HasNZParams(['to_add','to_delete'])
def modLibrary(request, player_id, player):
  try:
    toAdd = json.loads(request.POST['to_add'])
    toDelete = json.loads(request.POST['to_delete'])
  except ValueError:
    logger.error("Bad JSON. Couldn't even parse. \n" +
        "to add data: " + request.POST['to_add'] + "\n" +
        "to delete data: " + request.POST['to_delete'])
    return HttpResponseBadRequest("Bad JSON. Couldn't even parse. \n" +
      "to add data: " + request.POST['to_add'] + "\n" +
      "to delete data: " + request.POST['to_delete'])


  try:
    duplicates, badIds = getDuplicateDifferentIds(toAdd, player)
    if len(badIds) > 0:
      return HttpJSONResponse(json.dumps(badIds), status=409)

    nonExistentIds = getNonExistantLibIds(toDelete, player)
    if len(nonExistentIds) > 0:
      return HttpJSONResponse(json.dumps(nonExistentIds), status=404)

    addSongs(filter(lambda song: song['id'] not in duplicates, toAdd), player)
    deleteSongs(toDelete, player)
  except KeyError as e:
    return HttpResponseBadRequest('Bad JSON.\n Bad key: ' + str(e) )
  except ValueError as f:
    return HttpResponseBadRequest('Bad JSON.\n Bad value: ' + str(f) )

  return HttpResponse()
