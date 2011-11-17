import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.models import Event
from udj.JSONCodecs import getJSONForEvents


@AcceptsMethods('GET')
@TicketUserMatch
def getNearbyEvents(request, latitude, longitude):
  events = Event.objects.all()
  events_json = getJSONForEvents(events)
  return HttpResponse(events_json)  
