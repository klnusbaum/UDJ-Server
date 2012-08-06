import json

from udj.models import Participant, PlayerPassword
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER, FORBIDDEN_REASON_HEADER
from udj.views.views06.decorators import PlayerExists, PlayerIsActive, AcceptsMethods, UpdatePlayerActivity, HasNZParams
from udj.views.views06.authdecorators import NeedsAuth, IsOwnerOrParticipates
from udj.views.views06.auth import getUserForTicket, hashPlayerPassword
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime

@csrf_exempt
@AcceptsMethods(['PUT'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
def participateWithPlayer(request, player_id, player):

  def onSuccessfulPlayerAuth(activePlayer, user):
    #very important to check if they're banned or player is full first.
    #otherwise we might might mark them as actually participating
    if Participant.objects.filter(user=user, player=activePlayer, ban_flag=True).exists():
      toReturn = HttpResponseForbidden()
      toReturn[FORBIDDEN_REASON_HEADER] = 'banned'
      return toReturn
    if activePlayer.isFull():
      toReturn = HttpResponseForbidden()
      toReturn[FORBIDDEN_REASON_HEADER] = 'player-full'
      return toReturn

    obj, created = Participant.objects.get_or_create(player=activePlayer, user=user)
    if not created:
      obj.time_last_interation = datetime.now()
      obj.kick_flag = False
      obj.save()

    return HttpResponse(status=201)


  user = getUserForTicket(request)
  playerPassword = PlayerPassword.objects.filter(player=player)
  if playerPassword.exists():
    if DJANGO_PLAYER_PASSWORD_HEADER in request.META:
      hashedPassword = hashPlayerPassword(request.META[DJANGO_PLAYER_PASSWORD_HEADER])
      if hashedPassword == playerPassword[0].password_hash:
        return onSuccessfulPlayerAuth(player, user)

    toReturn = HttpResponse(status=401)
    toReturn['WWW-Authenticate'] = 'player-password'
    return toReturn
  else:
    return onSuccessfulPlayerAuth(player, user)

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getUsersForPlayer(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.ActiveParticipants(), cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getAdminsForPlayer(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.Admins(), cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getSongSetsForPlayer(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.SongSets(), cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@HasNZParams(['query'])
def getAvailableMusic(request, player_id, player):
  availableMusic = player.AvailableMusic(request.GET['query'])
  if 'max_results' in request.GET:
    availableMusic = availableMusic[:request.GET['max_results']]
  return HttpJSONResponse(json.dumps(availableMusic, cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtists(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.Artists(), cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtistSongs(request, player_id, player, givenArtist):
  return HttpJSONResponse(json.dumps(player.ArtistSongs(givenArtist), cls=UDJEncoder))

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRecentlyPlayed(request, player_id, player):
  songs_limit = int(request.GET.get('max_songs',40))
  songs_limit = min(songs_limit,100)
  recentlyPlayed = player.RecentlyPlayed()[:songs_limit]
  return HttpJSONResponse(json.dumps(recentlyPlayed, cls=UDJEncoder))
