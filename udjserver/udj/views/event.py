import json
import hashlib
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
from udj.decorators import IsUserOrHost
from udj.models import Event
from udj.models import LibraryEntry
from udj.models import AvailableSong
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import UpVote
from udj.models import DownVote
from udj.JSONCodecs import getEventDictionary
from udj.JSONCodecs import getJSONForEvents
from udj.JSONCodecs import getJSONForAvailableSongs
from udj.JSONCodecs import getJSONForCurrentSong
from udj.JSONCodecs import getJSONForEventGoers


def getEventHost(event_id):
  return Event.objects.get(pk=event_id).host

@NeedsAuth
@AcceptsMethods('GET')
def getEvents(request):
  if not request.GET.__contains__('name'):
    return HttpResponseBadRequest("Must include name parameter")
  events = Event.objects.filter(name__icontains=request.GET['name'])
  events_json = getJSONForEvents(events)
  return HttpResponse(events_json)
  

@NeedsAuth
@AcceptsMethods('GET')
def getNearbyEvents(request, latitude, longitude):
  #TODO actually have this only return nearby events
  events = Event.objects.all()
  events_json = getJSONForEvents(events)
  return HttpResponse(events_json)  

@NeedsAuth
@AcceptsMethods('PUT')
@NeedsJSON
@IsntCurrentlyHosting
def createEvent(request):
  user = getUserForTicket(request)
  event = json.loads(request.raw_post_data)

  if 'name' not in event:
    return HttpResponseBadRequest("Must include a name attribute")
  toInsert = Event(name=event['name'], host=user)

  if 'coords' in event:
    if 'latitude' not in event['coords'] or 'longitude' not in event['coords']:
      return HttpResponseBadRequest("Must include both latitude and "
        "longitude with coords")
    else:
      toInsert.latitude = event['coords']['latitude']
      toInsert.longitude = event['coords']['longitude']

  if 'password' in event:
    m = hashlib.sha1()
    m.update(event[password])
    toInsert.password_hash = m.hexdigest()
      
  toInsert.save()
  
  hostInsert = EventGoer(user=user, event=toInsert)
  hostInsert.save()
  return HttpResponse('{"event_id" : ' + str(event.id) + '}', status=201)

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
  toEnd.time_ended = datetime.datetime.now()
  toEnd.save()
  return HttpResponse("Party ended")

@NeedsAuth
@TicketUserMatch
@AcceptsMethods(['PUT', 'DELETE'])
def joinOrLeaveEvent(request, event_id, user_id):
  if request.method == 'PUT':
    return joinEvent(request, event_id, user_id)
  elif request.method == 'DELETE':
    return leaveEvent(request, event_id, user_id)



@CanLoginToEvent
def joinEvent(request, event_id, user_id):
  joining_user = User.objects.get(pk=user_id)
  isAlreadyInEvent = EventGoer.objects.filter(user=joining_user)
  if isAlreadyInEvent.exists():
    if isAlreadyInEvent[0].event.id == int(event_id):
      return HttpResponse("joined event", status=201)
    else:
      return HttpResponse(
        json.dumps(getEventDictionary(isAlreadyInEvent[0].event)), status=409)
  event_to_join = Event.objects.get(pk=event_id)
  event_goer = EventGoer(user=joining_user, event=event_to_join)
  event_goer.save()
  return HttpResponse("joined event", status=201)

@InParty
def leaveEvent(request, event_id, user_id):
  event_goer = EventGoer.objects.get(event__id=event_id, user__id=user_id)
  event_goer.delete()
  return HttpResponse("left event")

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
    
  return HttpResponse(getJSONForAvailableSongs(available_songs))

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getRandomMusic(request, event_id):
  rand_limit = request.GET.get('max_randoms',20)
  randomSongs = AvailableSong.objects.filter(event__id=id)
  randomSongs = randomSongs.order_by('?')[:rand_limit]
  return HttpResponse(getJSONForAvailableSongs(randomSongs))

@IsEventHost
@NeedsJSON
def addToAvailableMusic(request, event_id):
  host = getUserForTicket(request)
  toAdd = json.loads(request.raw_post_data)
  added = []
  for song_id in toAdd:
    addSong = AvailableSong(song=LibraryEntry.objects.get(
      host_lib_song_id=song_id, owning_user=host))
    addSong.save()
    added.append(song_id)

  return HttpResponse(json.dumps(added), status=201)

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
@AcceptsMethods(['GET', 'POST'])
def currentSong(request, event_id):
  if request.method == 'GET':
    return getCurrentSong(request, event_id=event_id)
  else: 
    return setCurrentSong(request, event_id=event_id)

@InParty
def getCurrentSong(request, event_id):
  currentSong = get_object_or_404(
    ActivePlaylistEntry, event__id=event_id, state=u'PL')
  return HttpResponse(getJSONForCurrentSong(currentSong))

@IsEventHost
def setCurrentSong(request, event_id):
  if(not request.POST.__contains__('playlist_entry_id')):
    return HttpResponseBadRequest(
      'Please specifiy the playlist entry to set as the current song')

  event = Event.objects.get(event__id=event_id) 
  newCurrentSong = get_object_or_404(
    ActivePlaylistEntry, pk=request.POST.__get__('playlist_entry_id'))
  newCurrentSong.state=u'PL'

  currentSong = None
  try:
    currentSong = ActivePlaylistEntry.objects.get(
    event__id=event_id, state=u'PL')
    currentSong.state=u'FN'
    currentSong.save()
  except ObjectDoesNotExist:
    pass
  newCurrentSong.save()
  return HttpResponse("Song changed")

  
@NeedsAuth
@AcceptsMethods('GET')
@InParty
def getEventGoers(request, event_id):
  eventGoers = EventGoer.objects.filter(event__id=event_id)
  return HttpResponse(getJSONForEventGoers(eventGoers))

