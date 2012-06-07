import json

from udj.decorators import NeedsJSON
from udj.decorators import AcceptsMethods
from udj.decorators import PlayerExists
from udj.decorators import HasNZParams
from udj.authdecorators import NeedsAuth
from udj.authdecorators import TicketUserMatch
from udj.models import LibraryEntry
from udj.models import Player
from udj.headers import MISSING_RESOURCE_HEADER

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

def getAlreadyExistingIds(songs, player):
  existingIds = []
  for song in songs:
    if LibraryEntry.objects.filter(player=player, player_lib_song_id=song['id'], is_deleted=False).exists():
      existingIds.append(song['id'])
  return existingIds

def getNonExistantIds(songIds, player):
  nonExistentIds = []
  for songId in songIds:
    if not LibraryEntry.objects.filter(player=player, player_lib_song_id=songId, is_deleted=False).exists():
      nonExistentIds.append(songId)
  return nonExistentIds


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

@csrf_exempt
@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['PUT'])
@NeedsJSON
@PlayerExists
@transaction.commit_on_success
def addSongs2Library(request, user_id, player_id, player):

  try:
    libJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  try:
    existingIds = getAlreadyExistingIds(libJSON, player)
    if len(existingIds) > 0:
      return HttpResponse(json.dumps(existingIds), status=409)
    addSongs(libJSON, player)
  except KeyError as e:
    return HttpResponseBadRequest("Bad JSON. Missing key: " + str(e))
  except ValueError as f:
    return HttpResponseBadRequest("Bad JSON. Bad value: " + str(f))

  return HttpResponse(status=201)

@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['DELETE'])
@PlayerExists
def deleteSongFromLibrary(request, user_id, player_id, lib_id, player):
  try:
    deleteSongs([lib_id], player)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse()

@csrf_exempt
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

@csrf_exempt
@NeedsAuth
@TicketUserMatch
@PlayerExists
@AcceptsMethods(['POST'])
@transaction.commit_on_success
@HasNZParams(['to_add','to_delete'])
def modLibrary(request, user_id, player_id, player):
  try:
    toAdd = json.loads(request.POST['to_add'])
    toDelete = json.loads(request.POST['to_delete'])
  except ValueError:
    return HttpResponseBadRequest("Bad JSON. Couldn't even parse. \n" +
      "to add data: " + request.POST['to_add'] + "\n" +
      "to delete data: " + request.POST['to_delete'])


  try:
    existingIds = getAlreadyExistingIds(toAdd, player)
    if len(existingIds) > 0:
      return HttpResponse(json.dumps(existingIds), status=409)

    nonExistentIds = getNonExistantIds(toDelete, player)
    if len(nonExistentIds) > 0:
      return HttpResponse(json.dumps(nonExistentIds), status=404)

    addSongs(toAdd, player)
    deleteSongs(toDelete, player)
  except KeyError as e:
    return HttpResponseBadRequest('Bad JSON.\n Bad key: ' + str(e) )
  except ValueError as f:
    return HttpResponseBadRequest('Bad JSON.\n Bad value: ' + str(f) )

  return HttpResponse()
