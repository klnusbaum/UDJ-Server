import json

from udj.models import Participant, Player, ActivePlaylistEntry, LibraryEntry, Vote
from udj.views.views06.decorators import PlayerExists, PlayerIsActive, AcceptsMethods, UpdatePlayerActivity, HasNZParams
from udj.views.views06.authdecorators import NeedsAuth, IsOwnerOrParticipates, IsOwnerOrParticipatingAdmin
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse
from udj.views.views06.auth import getUserForTicket
from udj.headers import MISSING_RESOURCE_HEADER

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

def getAlreadyOnPlaylist(libIds, library, player):
  return filter(lambda x: return ActivePlaylistEntry.isQueuedOrPlaying(x, library, player), libIds)

def getNotOnPlaylist(libIds, library, player):
  return filter(lambda x: return not ActivePlaylistEntry.isQueued(x, library, player), libIds)

def addSongsToPlaylist(libIds, library, activePlayer, user):
  for lib_id in libIds:
    libEntry = LibraryEntry.objects.get(library=library, lib_id=lib_id)

    addedEntry = ActivePlaylistEntry(song=libEntry, adder=user)
    addedEntry.save()

    Vote(playlist_entry=addedEntry, user=user, weight=1).save()

def removeSongsFromPlaylist(libIds, library, activePlayer, user):
  for lib_id in libIds:
    playlistEntry = ActivePlaylistEntry.objects.get(
      song__library=library,
      song__lib_id=lib_id,
      state='QE')
    playlistEntry.state='RM'
    playlistEntry.save()



@csrf_exempt
@AcceptsMethods(['GET', 'POST'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@transaction.commit_on_success
def activePlaylist(request, player_id, player):
  if request.method == 'GET':
    return getActivePlaylist(player)
  elif request.method == 'POST':
    return multiModActivePlaylist(request, player)
  else:
    #Should never get here because of the AcceptsMethods decorator
    #Put here because I'm pedantic sometimes :/
    return HttpResponseNotAllowed(['POST', 'DELETE'])

def getActivePlaylist(player):
  return HttpJSONResponse(json.dumps(player.ActivePlaylist(), cls=UDJEncoder))

@HasNZParams(['to_add','to_remove'])
def multiModActivePlaylist(request, player):
  player.lockActivePlaylist()
  try:
    toAdd = json.loads(request.POST['to_add'])
    toRemove = json.loads(request.POST['to_remove'])
  except ValueError:
    return HttpResponseBadRequest('Bad JSON\n. Couldn\'t even parse.\n Given data:' + request.raw_post_data)

  user = getUserForTicket(request)
  #Only admins and owners may remove songs from the playlist
  if len(toRemove) != 0 and not (player.isAdmin(user) or player.owning_user==user):
    return HttpResponseForbidden()

  try:
    #0. lock active playlist
    player.lockActivePlaylist()

    default_library = player.DefaultLibrary

    #first, validate/process all our inputs
    # 1. Ensure none of the songs to be deleted aren't on the playlist
    notOnPlaylist = getNotOnPlaylist(toRemove, default_library, player)
    if len(notOnPlaylist) > 0:
      toReturn = HttpJSONResponse(json.dumps(notOnPlaylist), status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    # 2. Ensure all of the songs to be added actually exists in the library
    notInLibrary = []
    for songId in toAdd:
      if not LibraryEntry.songExsitsAndNotBanned(songId, player):
        notInLibrary.append(songId)

    if len(notInLibrary) > 0:
      toReturn = HttpJSONResponse(json.dumps(notInLibrary), content_type="text/json", status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    # 3. See if there are any songs that we're trying to add that are already on the playlist
    # and vote them up instead.
    alreadyOnPlaylist = getAlreadyOnPlaylist(toAdd, default_library, player)
    toAdd = filter(lambda x: x not in alreadyOnPlaylist, toAdd)
    try:
      currentSong = ActivePlaylistEntry.objects.get(song__player=player, state='PL')
    except ObjectDoesNotExist:
      currentSong = None
    for libid in alreadyOnPlaylist:
      #make sure we don't vote on the currently playing song
      if currentSong != None and currentSong.song.player_lib_song_id != libid:
        voteSong(player, user, libid, 1)

    #alright, should be good to go. Let's actually add/remove songs
    #Note that we didn't make any actual changes to the DB until we were sure all of our inputs
    #were good and we weren't going to return an error HttpResponse. This is what allows us to use
    #the commit on success
    addSongsToPlaylist(toAdd, default_library, player, user)
    removeSongsFromPlaylist(toRemove, default_library, player, user)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))
  except TypeError:
    return HttpResponseBadRequest('Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))


  return HttpResponse()


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@transaction.commit_on_success
def modActivePlaylist(request, player_id, player, lib_id):
  user = getUserForTicket(request)
  if request.method == 'PUT':
    return add2ActivePlaylist(user, lib_id, player.DefaultLibrary, player)
  elif request.method == 'DELETE':
    if not (user == player.owning_user or player.isAdmin(user)):
      return HttpResponseForbidden()
    return removeFromActivePlaylist(request, user, lib_id, player.DefaultLibrary, player)


def add2ActivePlaylist(user, lib_id, default_library, player):
  player.lockActivePlaylist()
  if ActivePlaylistEntry.isQueued(lib_id, default_library, player):
    voteSong(player, user, lib_id, 1)
    return HttpResponse()
  elif ActivePlaylistEntry.isPlaying(lib_id, default_library, player):
    return HttpResponse()

  try:
    addSongsToPlaylist([lib_id], default_library, player, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse(status=201)

def removeFromActivePlaylist(request, user, lib_id, default_library, player):
  player.lockActivePlaylist()
  try:
    removeSongsFromPlaylist([lib_id], default_library, player, user)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  return HttpResponse()



@csrf_exempt
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST', 'PUT'])
def voteSongDown(request, player_id, lib_id, player):
  return voteSong(player, getUserForTicket(request), lib_id, -1)

@csrf_exempt
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST', 'PUT'])
def voteSongUp(request, player_id, lib_id, player):
  return voteSong(player, getUserForTicket(request), lib_id, 1)

def voteSong(player, user, lib_id, weight):

  try:
    playlistEntry = ActivePlaylistEntry.objects.get(
        song__player=player.DefaultLibrary,
        song__lib_id=lib_id,
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
