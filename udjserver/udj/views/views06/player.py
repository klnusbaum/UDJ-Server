import json
import math
from datetime import datetime

from udj.headers import MISSING_RESOURCE_HEADER
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER
from udj.models import Vote
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import ExternalLibrary
from udj.models import SortingAlgorithm
from udj.models import PlayerPassword
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.exceptions import LocationNotFoundError
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import PlayerExists
from udj.views.views06.decorators import ActivePlayerExists
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.authdecorators import IsOwnerOrParticipates
from udj.views.views06.authdecorators import IsOwner
from udj.views.views06.decorators import UpdatePlayerActivity
from udj.views.views06.auth import hashPlayerPassword
from udj.views.views06.auth import getUserForTicket
from udj.views.views06.JSONCodecs import UDJEncoder


from django.db import transaction
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
from django.contrib.gis.geos import Point




"""


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@ActivePlayerExists
@IsOwner
@HasNZParams(['lib_id'])
def setCurrentSong(request, player_id, activePlayer):

  try:
    changeCurrentSong(activePlayer, request.POST['lib_id'])
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn
  return HttpResponse("Song changed")


@transaction.commit_on_success
def changeCurrentSong(activePlayer, lib_id):
  #Make sure the song to be set exists
  newCurrentSong = ActivePlaylistEntry.objects.get(
    song__player_lib_song_id=lib_id, 
    song__player=activePlayer,
    state=u'QE')

  try:
    currentSong = ActivePlaylistEntry.objects.get(song__player=activePlayer, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    pass
  except MultipleObjectsReturned:
    ActivePlaylistEntry.objects.filter(song__player=activePlayer, state=u'PL').update(state=u'FN')

  newCurrentSong.state = u'PL'
  newCurrentSong.save()
  PlaylistEntryTimePlayed(playlist_entry=newCurrentSong).save()




def onSuccessfulPlayerAuth(activePlayer, user_id):
  obj, created = Participant.objects.get_or_create(player=activePlayer, user=User.objects.get(pk=user_id))
  if created:
    obj.time_last_interation = datetime.now()
    obj.save()
  return HttpResponse(status=201)

@csrf_exempt
@AcceptsMethods(['PUT'])
@NeedsAuth
@TicketUserMatch
@ActivePlayerExists
def participateWithPlayer(request, player_id, user_id, activePlayer):
  playerPassword = PlayerPassword.objects.filter(player=activePlayer)
  if playerPassword.exists():
    if DJANGO_PLAYER_PASSWORD_HEADER in request.META:
      hashedPassword = hashPlayerPassword(request.META[DJANGO_PLAYER_PASSWORD_HEADER])
      if hashedPassword == playerPassword[0].password_hash:
        return onSuccessfulPlayerAuth(activePlayer, user_id)

    toReturn = HttpResponse(status=401)
    toReturn['WWW-Authenticate'] = 'player-password'
    return toReturn
  else: 
    return onSuccessfulPlayerAuth(activePlayer, user_id)

@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getActiveUsersForPlayer(request, user, player_id, activePlayer):
  return HttpResponse(
    json.dumps(Participant.activeParticipants(activePlayer),
    cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@HasNZParams(['query'])
@UpdatePlayerActivity
def getAvailableMusic(request, user, player_id, activePlayer):
  query = request.REQUEST['query']
  available_songs = LibraryEntry.objects.filter(player=activePlayer).filter(
    Q(title__icontains=query) |
    Q(artist__icontains=query) |
    Q(album__icontains=query)).exclude(
        Q(is_deleted=True)|
        Q(is_banned=True))

  if 'max_results' in request.GET:
    available_songs = available_songs[:request.GET['max_results']]

  return HttpResponse(json.dumps(available_songs, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRandomMusic(request, user, player_id, activePlayer):
  rand_limit = int(request.GET.get('max_randoms',20))
  rand_limit = min(rand_limit,100)
  randomSongs = LibraryEntry.objects.filter(player=activePlayer) \
      .exclude(Q(is_deleted=True) | Q(is_banned=True))
  randomSongs = randomSongs.order_by('?')[:rand_limit]

  return HttpResponse(json.dumps(randomSongs, cls=UDJEncoder))


@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtists(request, user, player_id, activePlayer):
  artists = LibraryEntry.objects.filter(player=activePlayer)\
      .exclude(is_deleted=True)\
      .exclude(is_banned=True)\
      .distinct('artist').order_by('artist').values_list('artist', flat=True)
  return HttpResponse(json.dumps(artists, cls=UDJEncoder))


@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtistSongs(request, user, player_id, activePlayer, givenArtist):
  songs = LibraryEntry.objects.filter(player=activePlayer)\
      .exclude(is_deleted=True)\
      .exclude(is_banned=True)\
      .filter(artist=givenArtist)
  return HttpResponse(json.dumps(songs, cls=UDJEncoder))


@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRecentlyPlayed(request, user, player_id, activePlayer):
  songs_limit = int(request.GET.get('max_songs',20))
  songs_limit = min(songs_limit,100)
  songs = PlaylistEntryTimePlayed.objects.filter(playlist_entry__song__player=activePlayer)\
    .filter(playlist_entry__state='FN')\
    .order_by('-time_played')[:songs_limit]

  return HttpResponse(json.dumps([song.playlist_entry for song in songs], cls=UDJEncoder))
"""
