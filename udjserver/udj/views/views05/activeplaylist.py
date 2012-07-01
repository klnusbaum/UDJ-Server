import json

from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Vote
from udj.models import Player
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.views.views05.decorators import AcceptsMethods
from udj.views.views05.decorators import ActivePlayerExists
from udj.views.views05.decorators import UpdatePlayerActivity
from udj.views.views05.decorators import HasNZParams
from udj.views.views05.authdecorators import NeedsAuth
from udj.views.views05.authdecorators import TicketUserMatch
from udj.views.views05.authdecorators import IsOwnerOrParticipates
from udj.views.views05.JSONCodecs import UDJEncoder
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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def getAlreadyOnPlaylist(libIds, player):
  alreadyOnPlaylist = []
  for libId in libIds:
    if ActivePlaylistEntry.isQueuedOrPlaying(libId, player):
      alreadyOnPlaylist.append(libId)
  return alreadyOnPlaylist

def getNotOnPlaylist(libIds, player):
  notOnPlaylist = []
  for libId in libIds:
    if not ActivePlaylistEntry.isQueued(libId, player):
      notOnPlaylist.append(libId)
  return notOnPlaylist


def addSongsToPlaylist(libIds, activePlayer, user):
  for lib_id in libIds:
    libEntry = LibraryEntry.objects.get(player=activePlayer, player_lib_song_id=lib_id,
      is_deleted=False, is_banned=False)

    addedEntry = ActivePlaylistEntry(song=libEntry, adder=user)
    addedEntry.save()

    Vote(playlist_entry=addedEntry, user=user, weight=1).save()

def removeSongsFromPlaylist(libIds, activePlayer, user):
  for lib_id in libIds:
    playlistEntry = ActivePlaylistEntry.objects.get(
      song__player=activePlayer,
      song__player_lib_song_id=lib_id,
      state='QE')
    playlistEntry.state='RM'
    playlistEntry.save()


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['GET', 'POST'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def activePlaylist(request, user, player_id, activePlayer):
  if request.method == 'GET':
    return getActivePlaylist(request, user, player_id, activePlayer)
  elif request.method == 'POST':
    return multiModActivePlaylist(request, user, player_id, activePlayer)

def getActivePlaylist(request, user, player_id, activePlayer):
  queuedEntries = ActivePlaylistEntry.objects.filter(song__player=activePlayer, state='QE')
  queuedEntries = activePlayer.sortPlaylist(queuedEntries)
  playlist={'active_playlist' : queuedEntries}

  try:
    currentPlaying = ActivePlaylistEntry.objects.get(song__player=activePlayer, state='PL')
    playlist['current_song'] = currentPlaying
  except ObjectDoesNotExist, MultipleObjectsReturned:
    playlist['current_song'] = {}

  playlist['volume'] = activePlayer.volume
  playlist['state'] = 'playing' if activePlayer.state=='PL' else 'paused'

  return HttpResponse(json.dumps(playlist, cls=UDJEncoder), content_type="text/json")

@HasNZParams(['to_add','to_remove'])
@transaction.commit_on_success
def multiModActivePlaylist(request, user, player_id, activePlayer):
  if activePlayer.owning_user != user:
    return HttpResponseForbidden("Only the owner may do that")
  try:
    toAdd = json.loads(request.POST['to_add'])
    toRemove = json.loads(request.POST['to_remove'])
  except ValueError:
    return HttpResponseBadRequest('Bad JSON\n. Couldn\'t even parse.\n Given data:' + request.raw_post_data)

  try:

    #first, validate all our inputs
    # 1. Ensure none of the songs that want to be added are already on the playlist
    alreadyOnPlaylist = getAlreadyOnPlaylist(toAdd, activePlayer)
    if len(alreadyOnPlaylist) > 0:
      return HttpResponse(json.dumps(alreadyOnPlaylist), content_type="text/json", status=409)

    # 2. Ensure none of the songs to be deleted aren't on the playlist
    notOnPlaylist = getNotOnPlaylist(toRemove, activePlayer)
    if len(notOnPlaylist) > 0:
      toReturn = HttpResponse(json.dumps(notOnPlaylist), content_type="text/json", status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    # 3. Ensure all of the songs to be added actually exists in the library
    notInLibrary = []
    for songId in toAdd:
      if not LibraryEntry.songExsits(songId, activePlayer):
        notInLibrary.append(songId)

    if len(notInLibrary) > 0:
      toReturn = HttpResponse(json.dumps(notInLibrary), content_type="text/json", status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    addSongsToPlaylist(toAdd, activePlayer, user)
    removeSongsFromPlaylist(toRemove, activePlayer, user)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))
  except TypeError:
    return HttpResponseBadRequest('Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))


  return HttpResponse()


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def modActivePlaylist(request, user, player_id, lib_id, activePlayer):
  if request.method == 'PUT':
    return add2ActivePlaylist(user, lib_id, activePlayer)
  elif request.method == 'DELETE':
    if user != activePlayer.owning_user:
      return HttpResponseForbidden()
    return removeFromActivePlaylist(user, lib_id, activePlayer)


@transaction.commit_on_success
def add2ActivePlaylist(user, lib_id, activePlayer):

  if ActivePlaylistEntry.isQueuedOrPlaying(lib_id, activePlayer):
    return HttpResponse(status=409)

  try:
    addSongsToPlaylist([lib_id], activePlayer, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse(status=201)

@transaction.commit_on_success
def removeFromActivePlaylist(user, lib_id, activePlayer):
  try:
    removeSongsFromPlaylist([lib_id], activePlayer, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse()



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
