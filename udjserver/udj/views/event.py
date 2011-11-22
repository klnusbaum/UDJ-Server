import json
import hashlib
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import IsEventHost
from udj.decorators import CanLoginToEvent
from udj.decorators import IsUserOrHost
from udj.decorators import InParty
from udj.models import Event
from udj.models import AvailableSong
from udj.models import EventGoer
from udj.models import FinishedEvent
from udj.JSONCodecs import getJSONForEvents
from udj.auth import getUserForTicket
from udj.JSONCodecs import getJsonForLibraryEntry


@AcceptsMethods('GET')
@NeedsAuth
def getNearbyEvents(request, latitude, longitude):
  #TODO actually have this only return nearby events
  events = Event.objects.all()
  events_json = getJSONForEvents(events)
  return HttpResponse(events_json)  

@AcceptsMethods('PUT')
@NeedsJSON
@NeedsAuth
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
  return HttpResponse('{"event_id" : ' + str(toInsert.id) + '}', status=201)

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
  toDelete = Event.objects.filter(id=event_id)[0]
  finishedEvent = FinishedEvent(
    party_id = toDelete.id, 
    name=toDelete.name, 
    host=toDelete.host, 
    latitude = toDelete.latitude,
    longitude = toDelete.longitude,
     time_started = toDelete.time_started)
  toDelete.delete()
  finishedEvent.save() 
  return HttpResponse("Party ended")


@AcceptsMethods('PUT')
@NeedsAuth
@CanLoginToEvent
def joinEvent(request, event_id):
  joining_user = getUserForTicket(request)
  event_to_join = Event.objects.filter(id=event_id)[0]
  event_goer = EventGoer(user=joining_user, event=event_to_join)
  event_goer.save()
  return HttpResponse("joined event", status=201)

@AcceptsMethods('DELETE')
@NeedsAuth
@IsUserOrHost
def leaveEvent(request, event_id, user_id):
  event_goer = EventGoer.objects.filter(event__id=event_id, user__id=user_id)[0]
  event_goer.delete()
  return HttpResponse("left event")

@NeedsAuth
@InParty
@AcceptsMethods(['GET', 'PUT', 'DELETE'])
def availableMusic(request, event_id):
  if request.method == 'GET':
    return getAvailableMusic(request, event_id)


def getAvailableMusic(request, event_id):
  event = Event.objects.get(pk=event_id)
  if(not request.GET.__contains__('query')):
    return HttpResponseBadRequest('Must specify query')
  query = request.GET.__getitem__('query')
  #TODO Yes, I know this is dumb. There should be a more efficient way
  # to do this in one query.
  available_songs= AvailableSong.objects.filter(
    library_entry__owning_user=event.host, 
    library_entry__song__icontains=query)
  available_songs = available_songs | (AvailableSong.objects.filter(
    library_entry__owning_user=event.host, 
    library_entry__artist__icontains=query))
  available_songs= available_songs | (AvailableSong.objects.filter(
    library_entry__owning_user=event.host, 
    library_entry__album__icontains=query))
  toReturn = []
  for available_song in available_songs:
    toReturn.append(getJsonForLibraryEntry(available_song.library_entry))

  return HttpResponse(json.dumps(toReturn))

