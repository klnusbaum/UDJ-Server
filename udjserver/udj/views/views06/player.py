import json
import math
from datetime import datetime

from settings import geocodeLocation

from udj.headers import MISSING_RESOURCE_HEADER
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER
from udj.models import Vote
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import State
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
from udj.views.views06.authdecorators import TicketUserMatch
from udj.views.views06.authdecorators import IsOwnerOrParticipates
from udj.views.views06.authdecorators import IsOwner
from udj.views.views06.decorators import UpdatePlayerActivity
from udj.views.views06.auth import hashPlayerPassword
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
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D


def isValidLocation(location):
  return \
    'address' in location and \
    'city' in location and \
    'state' in location and \
    State.objects.filter(name__iexact=location['state']).exists() and \
    'zipcode' in location

@NeedsAuth
@AcceptsMethods(['GET'])
def getNearbyPlayers(request, latitude, longitude):
  givenLat = float(latitude)
  givenLon = float(longitude)
  point = Point(givenLon, givenLat)

  nearbyLocations = PlayerLocation.objects.exclude(player__state='IN').filter(
    point__distance_lte=(point, D(km=5))).distance(point).order_by('distance')[:100]

  nearbyPlayers = [location.player for location in nearbyLocations]

  return HttpResponse(json.dumps(nearbyPlayers, cls=UDJEncoder), content_type="text/json")

@NeedsAuth
@AcceptsMethods(['GET'])
@HasNZParams(['name'])
def getPlayers(request):
  players = Player.objects.filter(name__icontains=request.GET['name']).exclude(state='IN')
  return HttpResponse(json.dumps(players, cls=UDJEncoder), content_type="text/json")


def doLocationSet(address, city, state, zipcode, player):
  lat, lon = geocodeLocation(address, city, state, zipcode)
  PlayerLocation(
    player=player,
    address=address,
    city=city,
    state=State.objects.get(name__iexact=state),
    zipcode=zipcode,
    point=Point(lon, lat)
  ).save()

@csrf_exempt
@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['PUT'])
@NeedsJSON
@transaction.commit_on_success
def createPlayer(request, user_id):
  user = User.objects.get(pk=user_id)
  try:
    newPlayerJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  #Ensure the name attribute was provided with the JSON
  newPlayerName = ""
  try:
    newPlayerName = newPlayerJSON['name']
  except KeyError:
    return HttpResponseBadRequest('No name given')

  #Ensure that the suers doesn't already have a player with the given name
  conflictingPlayer = Player.objects.filter(owning_user=user, name=newPlayerName)
  if conflictingPlayer.exists():
    return HttpResponse('A player with that name already exists', status=409)

  #Create and save new player
  newPlayer = Player(owning_user=user, name=newPlayerName)
  newPlayer.save()

  #If password provided, create and save password
  if 'password' in newPlayerJSON:
    PlayerPassword(player=newPlayer, password_hash=hashPlayerPassword(newPlayerJSON['password'])).save()

  #If locaiton provided, geocode it and save it
  if 'location' in newPlayerJSON:
    location = newPlayerJSON['location']
    if isValidLocation(location):
      try:
        doLocationSet(location['address'], location['city'],
            location['state'], location['zipcode'], newPlayer)
      except LocationNotFoundError:
        return HttpResponseBadRequest('Location not found')
    else:
      return HttpResponseBadRequest('Bad location')

  return HttpResponse(json.dumps({'player_id' : newPlayer.id}), status=201, content_type="text/json")

@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsAuth
@TicketUserMatch
@PlayerExists
@HasNZParams(['name'])
def changePlayerName(request, user_id, player_id, player):
  givenName = request.POST['name']
  if givenName == '':
    return HttpResponseBadRequest("Bad name")
  if Player.objects.filter(owning_user__id=user_id, name=givenName).exists():
    return HttpResponse(status=409)

  player.name=givenName
  player.save()

  return HttpResponse()

@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@TicketUserMatch
@PlayerExists
def modifyPlayerPassword(request, user_id, player_id, player):
  if request.method == 'POST':
    return setPlayerPassword(request, user_id, player_id, player)
  elif request.method == 'DELETE':
    return deletePlayerPassword(request, user_id, player_id, player)

@HasNZParams(['password'])
def setPlayerPassword(request, user_id, player_id, player):
  givenPassword = request.POST['password']
  if givenPassword == '':
    return HttpResponseBadRequest("Bad password")

  hashedPassword = hashPlayerPassword(givenPassword)

  playerPassword , created = PlayerPassword.objects.get_or_create(
      player=player,
      defaults={'password_hash': hashedPassword})
  if not created:
    playerPassword.password_hash = hashedPassword
    playerPassword.save()

  return HttpResponse()

def deletePlayerPassword(request, user_id, player_id, player):
  try:
    toDelete = PlayerPassword.objects.get(player=player)
    toDelete.delete()
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'password'
    return toReturn

@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@TicketUserMatch
@PlayerExists
@HasNZParams(['address','city','state','zipcode'])
def setLocation(request, user_id, player_id, player):

  try:
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    zipcode = request.POST['zipcode']
    lat, lon = geocodeLocation(address, city, state, zipcode)
    playerLocation, created = PlayerLocation.objects.get_or_create(
      player=player,
      defaults={
        'address' : address,
        'city' : city,
        'state' : State.objects.get(name=state),
        'zipcode' : zipcode,
        'point' : Point(lon, lat)
      }
    )
    if not created:
      playerLocation.address = address
      playerLocation.city = city
      playerLocation.state = State.objects.get(name=state)
      playerLocation.zipcode = zipcode
      playerLocation.latitude = lat
      playerLocation.longitude = lon
      playerLocation.save()
    return HttpResponse()
  except LocationNotFoundError:
    return HttpResponseBadRequest('Bad location')


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



@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@TicketUserMatch
@PlayerExists
@HasNZParams(['state'])
def setPlayerState(request, user_id, player_id, player):
  givenState = request.POST['state']

  if givenState == u'paused':
    player.state = u'PA'
  elif givenState == u'playing':
    player.state = u'PL'
  elif givenState == u'inactive':
    player.state = u'IN'
  else:
    return HttpResponseBadRequest("Bad state given: " + givenState)

  player.save()
  return HttpResponse()

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@TicketUserMatch
@PlayerExists
@HasNZParams(['volume'])
def setPlayerVolume(request, user_id, player_id, player):
  try:
    newVolume = int(request.POST['volume'])
    if newVolume > 10 or newVolume < 0:
      return HttpResponseBadRequest()
    player.volume = newVolume
    player.save()
    return HttpResponse()
  except ValueError:
    return HttpResponseBadRequest('Bad volume: ' + request.POST['volume'])


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

