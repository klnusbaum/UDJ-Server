import json

from udj.models import Participant, PlayerPassword, ActivePlaylistEntry, PlaylistEntryTimePlayed, EnabledExternalLibrary
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER, FORBIDDEN_REASON_HEADER, MISSING_RESOURCE_HEADER
from udj.views.views06.decorators import PlayerExists, PlayerIsActive, AcceptsMethods, UpdatePlayerActivity, HasNZParams
from udj.views.views06.authdecorators import NeedsAuth, IsOwnerOrParticipates, IsOwnerOrParticipatingAdmin, IsntOwner
from udj.views.views06.auth import getUserForTicket, hashPlayerPassword
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from datetime import datetime
from importlib import import_module

@csrf_exempt
@AcceptsMethods(['PUT', 'DELETE'])
@NeedsAuth
@PlayerExists
@IsntOwner
def modPlayerParticiapants(request, player_id, player):
  if request.method == 'PUT':
    return participateWithPlayer(request, player_id, player)
  elif request.method == 'DELETE':
    return logoutOfPlayer(request, player_id, player)
  else:
    #Should never get here because of the AcceptsMethods decorator
    #Put here because I'm pedantic sometimes :/
    return HttpResponseNotAllowed(['PUT', 'DELETE'])


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
      obj.logout_flag = False
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

def logoutOfPlayer(request, player_id, player):
  user = getUserForTicket(request)

  try:
    toLogOut = Participant.objects.get(player=player, user=user)
    toLogOut.logout_flag = True
    toLogOut.save()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn

  return HttpResponse()


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
  query = request.GET['query']
  internalResults = player.AvailableMusic(query)
  externalResults = []
  for enabledExternalLibrary in EnabledExternalLibrary.objects.filter(player=player):
    resolver = import_module('udj.external_library_resolvers.' +
        enabledExternalLibrary.externalLibrary.external_lib_resolver_module)
    externalResults.extend(resolver.search(query))

  toReturn =[]

  if len(internalResults) ==0 and len(externalResults) >0:
    toReturn = externalResults
  elif len(internalResults) > 0 and len(externalResults)==0:
    toReturn = internalResults
  else:
    for x in internalResults:
      externalResults.insert(0,x)
    toReturn = externalResults


  if 'max_results' in request.GET:
    toReturn = toReturn[:int(request.GET['max_results'])]
  return HttpJSONResponse(json.dumps(toReturn, cls=UDJEncoder))


  """
  #if len(totalResults) >0:
  if len(internalResults) > 0:
    totalResults = list(internalResults).extend(totalResults)
  #else:
  #  totalResults = internalResults

  if 'max_results' in request.GET:
    totalResults = totalResults[:request.GET['max_results']]

  return HttpJSONResponse(json.dumps(totalResults, cls=UDJEncoder))
  """


@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getArtists(request, player_id, player):
  artists = player.Artists()
  totalResults = []
  for enabledExternalLibrary in EnabledExternalLibrary.objects.filter(player=player):
    resolver = import_module('udj.external_library_resolvers.' +
        enabledExternalLibrary.externalLibrary.external_lib_resolver_module)
    totalResults.extend(resolver.artists())

  totalResults.extend(artists)
  totalResults = sorted(totalResults)

  return HttpJSONResponse(json.dumps(totalResults, cls=UDJEncoder))

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

@AcceptsMethods(['GET'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
def getRandomSongsForPlayer(request, player_id, player):
  rand_limit = int(request.GET.get('max_randoms',40))
  rand_limit = min(rand_limit,100)
  randomSongs = player.Randoms()[:rand_limit]
  return HttpJSONResponse(json.dumps(randomSongs, cls=UDJEncoder))

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
      song__player_lib_song_id=request.POST['lib_id'],
      song__player=player,
      state=u'QE')
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  try:
    currentSong = ActivePlaylistEntry.objects.get(song__player=player, state=u'PL')
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
    currentSong = ActivePlaylistEntry.objects.get(song__player=player, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn
  return HttpResponse()



