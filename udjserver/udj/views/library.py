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
from django.db import transaction

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
@transaction.commit_on_success
def addSongs2Library(request, user_id, player_id, player):

  try:
    libJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')


  for libEntry in libJSON:
    try:
      if LibraryEntry.objects.filter(player=player, player_lib_song_id=libEntry['id']).exists():
        return HttpResponse(status=409)
      LibraryEntry(
        player=player,
        player_lib_song_id=libEntry['id'],
        title=libEntry['title'],
        artist=libEntry['artist'],
        album=libEntry['album'],
        genre=libEntry['genre'],
        track=libEntry['track'],
        duration=libEntry['duration']).save()
    except KeyError:
      return HttpResponseBadRequest('Bad JSON\n' + request.raw_post_data)
    except ValueError:
      return HttpResponseBadRequest('Bad JSON\n' + request.raw_post_data)

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


