import json
import math

from udj.headers import MISSING_RESOURCE_HEADER
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import State
from udj.models import BannedSong
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import PlayerExists
from udj.decorators import ActivePlayerExists
from udj.authdecorators import NeedsAuth
from udj.authdecorators import TicketUserMatch
from udj.authdecorators import IsOwnerOrParticipates
from udj.authdecorators import IsOwner
from udj.decorators import HasNZParams
from udj.JSONCodecs import UDJEncoder
from udj.exceptions import LocationNotFoundError
from udj.auth import hashPlayerPassword

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from httplib import HTTPConnection
from httplib import HTTPResponse


from settings import geocodeLocation


def isValidLocation(location):
  return \
    'address' in location and \
    'city' in location and \
    'state' in location and \
    State.objects.filter(name__iexact=location['state']).exists() and \
    'zipcode' in location

def getDistanceToLocation(eventLocation, lat2, lon2):
  lat1 = eventLocation.latitude
  lon1 = eventLocation.longitude
  radius = 6371 # km
  dlat = math.radians(lat2-lat1)
  dlon = math.radians(lon2-lon1)
  a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
      * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = radius * c
  return d

@NeedsAuth
@AcceptsMethods(['GET'])
def getNearbyPlayers(request, latitude, longitude):
  playerLocations = PlayerLocation.objects.exclude(player__state='IN')
  nearbyLocations = []
  lat2 = float(latitude)
  lon2 = float(longitude)
  for location in playerLocations:
    distance = getDistanceToLocation(location, lat2, lon2)
    if distance < 5:
      nearbyLocations.append(location)

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
    latitude=lat,
    longitude=lon
  ).save()

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
    playerLocation = PlayerLocation.objects.get(player=player)
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


@NeedsAuth
@AcceptsMethods(['POST'])
@ActivePlayerExists
@IsOwner
@HasNZParams(['lib_id'])
def setCurrentSong(request, player_id, activePlayer):
  try:
    currentSong = ActivePlaylistEntry.objects.get(song__player=activePlayer, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    pass

  try:
    newCurrentSong = ActivePlaylistEntry.objects.get(
      song__player_lib_song_id=request.POST['lib_id'], 
      song__player=activePlayer,
      state=u'QE')
    newCurrentSong.state = u'PL'
    newCurrentSong.save()
    PlaylistEntryTimePlayed(playlist_entry=newCurrentSong).save() 
    return HttpResponse("Song changed")
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

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
    return HttpResponseBadRequest()

  player.save()
  return HttpResponse()

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
    return HttpResponseBadRequest()


def onSuccessfulPlayerAuth(activePlayer, user_id):
  Participant.objects.get_or_create(player=activePlayer, user=User.objects.get(pk=user_id))
  return HttpResponse(status=201)

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
def getActiveUsersForPlayer(request, player_id, activePlayer):
  return HttpResponse(
    json.dumps(Participant.activeParticipants(activePlayer),
    cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
@HasNZParams(['query'])
def getAvailableMusic(request, player_id, activePlayer):
  query = request.REQUEST['query']
  available_songs = LibraryEntry.objects.filter(player=activePlayer).filter(
    Q(title__icontains=query) |
    Q(artist__icontains=query) |
    Q(album__icontains=query)).exclude(is_deleted=True).filter(bannedsong__isnull = True)

  if 'max_results' in request.GET:
    available_songs = available_songs[:request.GET['max_results']]

  return HttpResponse(json.dumps(available_songs, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
@ActivePlayerExists
@IsOwnerOrParticipates
def getRandomMusic(request, player_id, activePlayer):
  rand_limit = request.GET.get('max_randoms',20)
  rand_limit = max(rand_limit,100)
  randomSongs = LibraryEntry.objects.filter(player=activePlayer) \
      .exclude(is_deleted=True) \
      .filter(bannedsong__isnull = True)
  randomSongs = randomSongs.order_by('?')[:rand_limit]

  return HttpResponse(json.dumps(randomSongs, cls=UDJEncoder))



"""
import json
import hashlib
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.auth import getUserForTicket
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsUUID
from udj.decorators import NeedsAuth
from udj.decorators import IsEventHost
from udj.decorators import CanLoginToEvent
from udj.decorators import InParty
from udj.decorators import IsntCurrentlyHosting
from udj.decorators import IsntInOtherEvent
from udj.decorators import IsUserOrHost
from udj.decorators import IsntHost
from udj.models import EventGoer
from udj.models import Event
from udj.models import EventLocation
from udj.models import EventPassword
from udj.models import EventEndTime
from udj.models import LibraryEntry
from udj.models import AvailableSong
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.JSONCodecs import getEventDictionary
from udj.JSONCodecs import getJSONForEvents
from udj.JSONCodecs import getJSONForAvailableSongs
from udj.JSONCodecs import getJSONForEventGoers
from udj.JSONCodecs import getJSONForEventsByLocation
from udj.JSONCodecs import getActivePlaylistEntryDictionary
from udj.utils import getJSONResponse
from udj.headers import getGoneResourceHeader
from udj.headers import getDjangoUUIDHeader
from udj.headers import getEventPasswordHeader
from udj.headers import getDjangoEventPasswordHeader;


def getEventHost(event_id):
  return Event.objects.get(pk=event_id).host

@NeedsAuth
@AcceptsMethods('GET')
def getEvents(request):
  if not request.GET.__contains__('name'):
    return HttpResponseBadRequest("Must include name parameter")
  events = Event.objects.filter(
    name__icontains=request.GET['name'],
    state=u'AC')
  events_json = getJSONForEvents(events)
  return getJSONResponse(events_json)


@NeedsAuth
@AcceptsMethods('GET')
def getNearbyEvents(request, latitude, longitude):
  #TODO This is super ineeficient. We need to switch over to a geo database
  locations = EventLocation.objects.filter(event__state=u'AC')
  events_json = getJSONForEventsByLocation(
    latitude, longitude, locations)
  return getJSONResponse(events_json)  
  

@NeedsAuth
@AcceptsMethods('PUT')
@NeedsJSON
@IsntCurrentlyHosting
def createEvent(request):
  user = getUserForTicket(request)
  event = json.loads(request.raw_post_data)

  if 'name' not in event:
    return HttpResponseBadRequest("Must include a name attribute")
  newEvent = Event(name=event['name'], host=user)
  newEvent.save()

  if 'coords' in event:
    if 'latitude' not in event['coords'] or 'longitude' not in event['coords']:
      return HttpResponseBadRequest("Must include both latitude and "
        "longitude with coords")
    else:
      EventLocation(event=newEvent, latitude=event['coords']['latitude'],
        longitude=event['coords']['longitude']).save()

  if 'password' in event:
    m = hashlib.sha1()
    m.update(event['password'])
    EventPassword(event=newEvent, password_hash=m.hexdigest()).save()

  hostInsert = EventGoer(user=user, event=newEvent)
  hostInsert.save()
  return getJSONResponse('{"event_id" : ' + str(newEvent.id) + '}', status=201)

#Should be able to make only one call to the events table to ensure it:
# 1. Exsits
# 2. This user is the host
# 3. Moved it to finished events and delete it.
# Right now these are all done seperately. 
#This is a potental future optimization
@AcceptsMethods('DELETE')
@NeedsAuth
@IsEventHost
def endEvent(request, event_id):
  #TODO We have a race condition here. Gonna need to wrap this in a transaction
  #in the future
  toEnd = Event.objects.get(pk=event_id)
  if toEnd.state == u'FN':
    return HttpResponse("Party ended")
  toEnd.state = u'FN'
  toEnd.save()
  EventEndTime(event=toEnd).save()
  user = getUserForTicket(request) 
  host = EventGoer.objects.get(user=user, event__id=event_id)
  host.state=u'LE'
  host.save()
  return HttpResponse("Party ended")

@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['PUT', 'DELETE'])
@IsntHost
def joinOrLeaveEvent(request, event_id, user_id):
  if request.method == 'PUT':
    return joinEvent(request, event_id=event_id, user_id=user_id)
  elif request.method == 'DELETE':
    return leaveEvent(request, event_id=event_id, user_id=user_id)

def authEvent(request, event_id):
  password = EventPassword.objects.filter(event__id=event_id)

  if password.exists():
    if getDjangoEventPasswordHeader() in request.META:
      givenPassword = request.META[getDjangoEventPasswordHeader()]
      m = hashlib.sha1()
      m.update(givenPassword)
      hashedPassword = m.hexdigest()
      if hashedPassword == password[0].password_hash:
        return True, None
    return False, HttpResponseNotFound()
  else:
    return True, None

@IsntInOtherEvent
def joinEvent(request, event_id, user_id):

  authSuccessfull, httpResponse = authEvent(request, event_id)
  if not authSuccessfull:
    return httpResponse

  event_to_join = Event.objects.get(pk=event_id)
  if event_to_join.state == u'FN':
    response = HttpResponse(status=410)
    response[getGoneResourceHeader()] = "event"
    return response

  joining_user = User.objects.get(pk=user_id)
  event_goer , created = EventGoer.objects.get_or_create(
    user=joining_user, event=event_to_join)

  #needed in case the user has logged out and is now logging back in
  if not created:
    event_goer.state=u'IE'
    event_goer.save()

  return HttpResponse("joined event", status=201)

def leaveEvent(request, event_id, user_id):
  requestingUser = getUserForTicket(request)
  try:
    event_goer = EventGoer.objects.get(
      user=requestingUser, event__id=event_id)
    event_goer.state=u'LE';
    event_goer.save()
    return HttpResponse("left event")
  except ObjectDoesNotExist:
    return HttpResponseForbidden(
      "You must be logged into the party to do that")

@NeedsAuth
@AcceptsMethods(['GET', 'PUT'])
def availableMusic(request, event_id):
  if request.method == 'GET':
    return getAvailableMusic(request, event_id=event_id)
  else:
    return addToAvailableMusic(request, event_id=event_id)

@InParty
def getAvailableMusic(request, event_id):
  event = Event.objects.get(pk=event_id)
  if(not request.GET.__contains__('query')):
    return HttpResponseBadRequest('Must specify query')
  query = request.GET.__getitem__('query')
  if query=='':
    return HttpResponseBadRequest('Blank searches not allowed')
  available_songs = AvailableSong.objects.filter(
    event__id=event_id, song__owning_user=event.host).exclude(state=u'RM')
  available_songs = available_songs.filter(
    Q(song__title__icontains=query) |
    Q(song__artist__icontains=query) |
    Q(song__album__icontains=query))
  if(request.GET.__contains__('max_results')):
    available_songs = available_songs[:request.GET['max_results']]

  return getJSONResponse(getJSONForAvailableSongs(available_songs))

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getRandomMusic(request, event_id):
  rand_limit = request.GET.get('max_randoms',20)
  randomSongs = AvailableSong.objects.filter(event__id=event_id)
  randomSongs = randomSongs.order_by('?')[:rand_limit]
  return getJSONResponse(getJSONForAvailableSongs(randomSongs))

@IsEventHost
@NeedsJSON
@NeedsUUID
def addToAvailableMusic(request, event_id):
  event = get_object_or_404(Event, pk=event_id)
  uuid = request.META[getDjangoUUIDHeader()]
  toAdd = json.loads(request.raw_post_data)
  added = []
  for song_id in toAdd:
    songToAdd = LibraryEntry.objects.get(
      host_lib_song_id=song_id, owning_user=event.host, machine_uuid=uuid)
    addedSong , created = AvailableSong.objects.get_or_create(
        event=event, song=songToAdd, defaults={'state': u'AC'})
    added.append(song_id)

  return getJSONResponse(json.dumps(added), status=201)

@NeedsAuth
@AcceptsMethods('DELETE')
@IsEventHost
def removeFromAvailableMusic(request, event_id, song_id):
  toRemove = get_object_or_404(AvailableSong, song__host_lib_song_id=song_id, event__id=event_id)
  toRemove.state = u'RM'
  toRemove.save()
  ActivePlaylistEntry.objects.filter(song__host_lib_song_id=song_id, event__id=event_id).update(state=u'RM')
  return HttpResponse()


@csrf_exempt
@NeedsAuth
@AcceptsMethods('POST')
@IsEventHost
def setCurrentSong(request, event_id):
  if(not request.POST.__contains__('playlist_entry_id')):
    return HttpResponseBadRequest(
      'Please specifiy the playlist entry to set as the current song')

  currentSong = None
  try:
    currentSong = ActivePlaylistEntry.objects.get(
    event__id=event_id, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    pass

  newId = request.POST['playlist_entry_id']
  newCurrentSong = get_object_or_404(
    ActivePlaylistEntry, 
    pk=request.POST['playlist_entry_id'],
    event__id=event_id)
  newCurrentSong.state = u'PL'
  newCurrentSong.save()

  PlaylistEntryTimePlayed(playlist_entry=newCurrentSong).save() 

  return HttpResponse("Song changed")


@NeedsAuth
@AcceptsMethods('GET')
@InParty
def getEventGoers(request, event_id):
  eventGoers = EventGoer.objects.filter(event__id=event_id)
  return getJSONResponse(getJSONForEventGoers(eventGoers))
"""
