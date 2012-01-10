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
    m.update(event[password])
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

@IsntInOtherEvent
def joinEvent(request, event_id, user_id):

  event_to_join = Event.objects.get(pk=event_id)
  if event_to_join.state == u'FN':
    return HttpResponse(status=410)

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
  available_songs = AvailableSong.objects.filter(
    event__id=event_id, song__owning_user=event.host)
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
def addToAvailableMusic(request, event_id):
  event = get_object_or_404(Event, pk=event_id)
  toAdd = json.loads(request.raw_post_data)
  added = []
  for song_id in toAdd:
    songToAdd = LibraryEntry.objects.get(
      host_lib_song_id=song_id, owning_user=event.host)
    addedSong , created = AvailableSong.objects.get_or_create(
      event=event, song=songToAdd)
    added.append(song_id)

  return getJSONResponse(json.dumps(added), status=201)

@NeedsAuth
@AcceptsMethods('DELETE')
@IsEventHost
def removeFromAvailableMusic(request, event_id, song_id):
  host = getUserForTicket(request)
  try:
    AvailableSong.objects.get(
      song__host_lib_song_id=song_id,
      song__owning_user=host).delete()
  except DoesNotExist:
    return HttpResponseNotFound("id " + str(song_id) + " doesn't exist")
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

