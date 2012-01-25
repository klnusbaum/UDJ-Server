import json
from udj.auth import isValidTicket
from udj.auth import ticketMatchesUser
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from udj.models import Event
from udj.models import EventGoer
from udj.auth import getUserForTicket
from django.shortcuts import get_object_or_404
from udj.headers import getTicketHeader
from udj.headers import getDjangoTicketHeader
from udj.headers import getGoneResourceHeader
from udj.JSONCodecs import getEventDictionary

def IsntHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    event_id = kwargs['event_id']
    event = Event.objects.get(pk=event_id)
    if event.host.id == user_id:
      return HttpResponseBadRequest("Hosts can't do that on their own event")
    else:
      return function(*args, **kwargs)
  return wrapper

def IsUserOrHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    event_id = kwargs['event_id']
    event = Event.objects.get(event_id__id=event_id)
    if ticketMatchesUser(args[0], user_id):
      return function(*args, **kwargs)
    elif event.host.id == user_id:
        return function(*args, **kwargs)
    else:
      return HttpResponseForbidden("only the host or user may do that")


def IsntCurrentlyHosting(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    hosts = Event.objects.filter(host=user).exclude(state__exact=u'FN')
    if hosts.exists():
      return HttpResponse(status=409)
    else:
      return function(*args, **kwargs)
  return wrapper
   
def InParty(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    event_id = kwargs['event_id'] 
    requestingUser = getUserForTicket(request)
    event_goers = EventGoer.objects.filter(
      user=requestingUser, event__id=event_id,
      state=u'IE')
    if not event_goers.exists():
      return HttpResponseForbidden(
        "You must be logged into the party to do that")
    elif event_goers[0].event.state == u'FN':
      response = HttpResponse(status=410)
      response[getGoneResourceHeader()] = "event"
      return response
    else:
      return function(*args, **kwargs)
  return wrapper


#TODO actually implement this fucntion. i.e. check for password compliance
def CanLoginToEvent(function):
  def wrapper(*args, **kwargs):
    return function(*args, **kwargs)
  return wrapper


def IsEventHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    event_id = kwargs['event_id']
    user = getUserForTicket(request)
    event = get_object_or_404(Event, pk=event_id)
    if event.host != user:
      return HttpResponseForbidden("Only the host of that event may do that")
    else:
      return function(*args, **kwargs)
  return wrapper

def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if getDjangoTicketHeader() not in request.META:
      responseString = "Must provide the " + getTicketHeader() + " header. "
      return HttpResponseBadRequest(responseString)
    elif not isValidTicket(
      request.META[getDjangoTicketHeader()], 
      request.META['REMOTE_ADDR']):
      return HttpResponseForbidden("Invalid ticket: \"" + 
        request.META[getDjangoTicketHeader()] + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper
      
def IsntInOtherEvent(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    event_id = kwargs['event_id']
    user_id = kwargs['user_id']
    eventLogins = \
      EventGoer.objects.exclude(event__id=event_id).filter(
      user__id=user_id, state=u'IE')
    if eventLogins.exists():
      return HttpResponse(
        json.dumps(getEventDictionary(eventLogins[0].event)), 
        status=409,
        content_type="text/json")
    else:
      return function(*args, **kwargs)
  return wrapper

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    if getDjangoTicketHeader() not in request.META:
      responseString = "Must provide the " + getTicketHeader() + " header. "
      return HttpResponseBadRequest(responseString)
    elif not isValidTicket(
      request.META[getDjangoTicketHeader()],
      request.META['REMOTE_ADDR']):
      return HttpResponseForbidden("Invalid ticket: \"" + 
        request.META[getDjangoTicketHeader()] + "\"")
    elif not ticketMatchesUser(request, user_id):
      return HttpResponseForbidden("The ticket doesn't match the given user\n" +
        "Give Ticket: \"" + request.META[getDjangoTicketHeader()] + "\"\n" +
        "Given User id: \"" + user_id + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper

def AcceptsMethods(acceptedMethods):
  def decorator(target):
    def wrapper(*args, **kwargs):
      request = args[0]
      if request.method in acceptedMethods:
        return target(*args, **kwargs)
      else:
        return HttpResponseNotAllowed(acceptedMethods)
    return wrapper
  return decorator
      
def NeedsJSON(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if not request.META.has_key('CONTENT_TYPE'):
      return HttpResponseBadRequest("must specify content type")
    elif request.META['CONTENT_TYPE'] != 'text/json':
      return HttpResponseBadRequest("must send json")
    elif request.raw_post_data == '':
      return HttpResponseBadRequest("didn't send anything. empty payload")
    else:
      return function(*args, **kwargs)
  return wrapper
    
    
