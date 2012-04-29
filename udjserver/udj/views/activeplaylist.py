import json

from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Vote
from udj.models import Player
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.decorators import AcceptsMethods
from udj.decorators import ActivePlayerExists
from udj.decorators import UpdatePlayerActivity
from udj.decorators import HasNZParams
from udj.authdecorators import NeedsAuth
from udj.authdecorators import TicketUserMatch
from udj.authdecorators import IsOwnerOrParticipates
from udj.JSONCodecs import UDJEncoder
from udj.exceptions import AlreadyExistsError
from udj.exceptions import ForbiddenError

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from settings import sortActivePlaylist

def addSongsToPlaylist(libIds, activePlayer, user):
  for lib_id in libIds:
    libEntry = LibraryEntry.objects.get(player=activePlayer, player_lib_song_id=lib_id,
      is_deleted=False, is_banned=False)

    if ActivePlaylistEntry.objects.filter(song=libEntry)\
      .exclude(state='RM').exclude(state='FN').exists():
      raise AlreadyExistsError("Song already on playlist")

    addedEntry = ActivePlaylistEntry(song=libEntry, adder=user)
    addedEntry.save()

    Vote(playlist_entry=addedEntry, user=user, weight=1).save()

def removeSongsFromPlaylist(libIds, activePlayer, user):
  for lib_id in libIds:
    playlistEntry = ActivePlaylistEntry.objects.get(
      song__player=activePlayer,
      song__player_lib_song_id=lib_id,
      state='QE')
    if user!=activePlayer.owning_user and user!=playlistEntry.adder:
      raise ForbiddenError("You're not the owner or adder of this song")
    playlistEntry.state='RM'
    playlistEntry.save()





@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getActivePlaylist(request, user, player_id, activePlayer):
  queuedEntries = ActivePlaylistEntry.objects.filter(song__player=activePlayer, state='QE')
  queuedEntries = sortActivePlaylist(queuedEntries)
  playlist={'active_playlist' : queuedEntries}

  try:
    currentPlaying = ActivePlaylistEntry.objects.get(song__player=activePlayer, state='PL')
    playlist['current_song'] = currentPlaying
  except ObjectDoesNotExist:
    playlist['current_song'] = {}

  return HttpResponse(json.dumps(playlist, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def modActivePlaylist(request, user, player_id, lib_id, activePlayer):
  if request.method == 'PUT':
    return add2ActivePlaylist(user, lib_id, activePlayer)
  elif request.method == 'DELETE':
    return removeFromActivePlaylist(user, lib_id, activePlayer)


@transaction.commit_on_success
def add2ActivePlaylist(user, lib_id, activePlayer):

  try:
    addSongsToPlaylist([lib_id], activePlayer, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn
  except AlreadyExistsError:
    return HttpResponse(status=409)

  return HttpResponse(status=201)

def removeFromActivePlaylist(user, lib_id, activePlayer):
  try:
    removeSongsFromPlaylist([lib_id], activePlayer, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn
  except ForbiddenError:
    return HttpResponseForbidden()

  return HttpResponse()

"""
@NeedsAuth
@AcceptsMethods(['POST'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
@HasNZParams(['to_add','to_remove'])
@transaction.commit_on_success
def multiModActivePlaylist(request, user, player_id, activePlayer):
  try:
    toAdd = json.loads(request.POST['to_add'])
    toDelete = json.loads(request.POST['to_remove'])

    addSongsToPlaylist(toAdd)
    removeSongsFromPlaylist(to_remove)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON\n' + request.raw_post_data)
  except AlreadyExistsError:
    return HttpResponse(status=409)

  return HttpResponse()
"""



@csrf_exempt
@NeedsAuth
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST'])
def voteSongDown(request, player_id, activePlayer, user_id, user, lib_id):
  return voteSong(activePlayer, user, lib_id, -1)

@csrf_exempt
@NeedsAuth
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST'])
def voteSongUp(request, player_id, activePlayer, user_id, user, lib_id):
  return voteSong(activePlayer, user, lib_id, 1)

def voteSong(activePlayer, user, lib_id, weight):

  try:
    playlistEntry = ActivePlaylistEntry.objects.get(
        song__player=activePlayer,
        song__player_lib_song_id=lib_id,
        state='QE')
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  vote, created = Vote.objects.get_or_create(playlist_entry=playlistEntry, user=user,
      defaults={'weight': weight})

  if not created:
    vote.weight = weight
    vote.save()

  return HttpResponse()
