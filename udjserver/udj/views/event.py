import json
import hashlib
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import IsEventHost
from udj.models import Event
from udj.models import FinishedEvent
from udj.JSONCodecs import getJSONForEvents
from udj.auth import getUserForTicket


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
    longitude = toDelete.longitude)
  toDelete.delete()
  finishedEvent.save() 
  return HttpResponse("Party ended")

