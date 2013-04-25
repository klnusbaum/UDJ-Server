import json
from udj.models import hashPlayerPassword, PlayerPassword, Participant
from udj.headers import FORBIDDEN_REASON_HEADER
from udj.views.views07.authdecorators import NeedsAuth, IsntOwner, HasPlayerPermissions, IsOwnerOrParticipates
from udj.views.views07.decorators import PlayerExists, PlayerIsActive, AcceptsMethods, UpdatePlayerActivity, HasNZJSONParams, NeedsJSON, HasNZParams
from udj.views.views07.responses import HttpJSONResponse, HttpResponseMissingResource
from udj.views.views07.JSONCodecs import UDJEncoder
from settings import DEFAULT_MAX_SONGS_RESULTS, DEFAULT_MAX_ARTIST_RESULTS
from itertools import islice


from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
"""
import json


from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


"""

@csrf_exempt
@AcceptsMethods(['PUT', 'DELETE'])
@NeedsAuth
@PlayerExists
@IsntOwner
def modPlayerParticiapants(request, player_id, player):
  if request.method == 'PUT':
    return participateWithPlayer(request, player_id, player)
  else:
    return logoutOfPlayer(request, player_id, player)

@PlayerIsActive
@HasPlayerPermissions(['PWP'], 2)
def participateWithPlayer(request, player_id, player):
  """
  This code is terrible. It's just ugly. But I can't see a better way to do it.
  My sincerest apologies.
  """

  def onSuccessfulPlayerAuth(activePlayer, user):
    #very important to check if they're banned or player is full first.
    #otherwise we might might mark them as actually participating
    if Participant.objects.filter(user=user, player=activePlayer, ban_flag=True).exists():
      toReturn = HttpResponseForbidden()
      toReturn[FORBIDDEN_REASON_HEADER] = 'banned'
      return toReturn
    if activePlayer.IsFull:
      toReturn = HttpResponseForbidden()
      toReturn[FORBIDDEN_REASON_HEADER] = 'player-full'
      return toReturn

    obj, created = Participant.objects.get_or_create(player=activePlayer, user=user)
    if not created:
      obj.time_last_interation = datetime.now()
      obj.kick_flag = False
      obj.logout_flag = False
      obj.save()

    return HttpResponse(status=201)


  user = request.udjuser
  playerPassword = PlayerPassword.objects.filter(player=player)
  if playerPassword.exists():
    hashedPassword = ""
    if not request.META.has_key('CONTENT_TYPE'):
      return HttpResponseBadRequest("must specify content type")
    elif request.META['CONTENT_TYPE'] != 'text/json':
      return HttpResponse("must send json", status=415)
    elif request.raw_post_data == '':
      return HttpResponseBadRequest("Bad JSON")
    try:
      password_json = json.loads(request.raw_post_data)
      password = password_json['password']
      hashedPassword = hashPlayerPassword(password)
    except ValueError:
      return HttpResponseBadRequest('Bad JSON')

    if hashedPassword == playerPassword[0].password_hash:
      return onSuccessfulPlayerAuth(player, user)


    toReturn = HttpResponse(status=401)
    toReturn['WWW-Authenticate'] = 'player-password'
    return toReturn
  else:
    return onSuccessfulPlayerAuth(player, user)

def logoutOfPlayer(request, player_id, player):
  user = request.udjuser

  try:
    toLogOut = Participant.objects.get(player=player, user=user)
    toLogOut.logout_flag = True
    toLogOut.save()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('user')

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getUsersForPlayer(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.ActiveParticipants, cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@HasNZParams(['query'])
def getAvailableMusic(request, player_id, player):
  query = request.GET['query']
  available_music = player.AvailableMusic(query)
  limit = int(request.GET.get('max_results', DEFAULT_MAX_SONGS_RESULTS))
  available_music = [x for x in islice(available_music, limit)]
  return HttpJSONResponse(json.dumps(available_music, cls=UDJEncoder))



@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtists(request, player_id, player):
  limit = int(request.GET.get('max_results', DEFAULT_MAX_ARTIST_RESULTS))
  artists = [x for x in islice(player.Artists, 0, limit)]
  return HttpJSONResponse(json.dumps(artists, cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtistSongs(request, player_id, player, givenArtist):
  toReturn = player.ArtistSongs(givenArtist)
  limit = int(request.GET.get('max_results', DEFAULT_MAX_ARTIST_RESULTS))
  return HttpJSONResponse(json.dumps(toReturn[:limit], cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRecentlyPlayed(request, player_id, player):
  songs_limit = int(request.GET.get('max_songs',40))
  songs_limit = min(songs_limit,100)
  recentlyPlayed = player.RecentlyPlayed[:songs_limit]
  return HttpJSONResponse(json.dumps(recentlyPlayed, cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRandomSongsForPlayer(request, player_id, player):
  rand_limit = int(request.GET.get('max_randoms',40))
  rand_limit = min(rand_limit,100)
  randomSongs = player.Randoms[:rand_limit]
  return HttpJSONResponse(json.dumps(randomSongs, cls=UDJEncoder))

"""
@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipatingAdmin
@UpdatePlayerActivity
@transaction.commit_on_success()
def modCurrentSong(request, player_id, player):
  if request.method == 'POST':
    return setCurrentSong(request, player)
  elif request.method == 'DELETE':
    return removeCurrentSong(request, player)
  else:
    #Should never get here because of the AcceptsMethods decorator
    #Put here because I'm pedantic sometimes :/
    return HttpResponseNotAllowed(['POST', 'DELETE'])

@HasNZParams(['lib_id'])
def setCurrentSong(request, player):
  player.lockActivePlaylist()
  try:
    newCurrentSong = ActivePlaylistEntry.objects.get(
      song__lib_id=request.POST['lib_id'],
      song__library=player.DefaultLibrary,
      state=u'QE')
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  try:
    currentSong = ActivePlaylistEntry.objects.get(song__library=player.DefaultLibrary, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    pass
  except MultipleObjectsReturned:
    #We should never get this, but some how we do sometimes. This is bad. It means that
    #this function isn't getting execute atomically like we hoped it would be
    #I think we may actually need a mutex to protect this critial section :(
    ActivePlaylistEntry.objects.filter(song__player=player, state=u'PL').update(state=u'FN')

  newCurrentSong.state = u'PL'
  newCurrentSong.save()
  PlaylistEntryTimePlayed(playlist_entry=newCurrentSong).save()
  return HttpResponse("Song changed")

def removeCurrentSong(request, player):
  player.lockActivePlaylist()
  try:
    currentSong = ActivePlaylistEntry.objects.get(song__library=player.DefaultLibrary, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn
  return HttpResponse()

"""
