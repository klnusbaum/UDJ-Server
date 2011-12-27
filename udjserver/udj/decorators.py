from udj.auth import isValidTicket
from udj.auth import ticketMatchesUser
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from udj.models import Event
from udj.models import EventGoer
from udj.models import FinishedEvent
from udj.auth import getUserForTicket
from django.shortcuts import get_object_or_404
from udj.headers import getTicketHeader
from udj.headers import getDjangoTicketHeader

def IsUserOrHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id'] if 'user_id' in kwargs else args[2]
    event_id = kwargs['event_id'] if 'event_id' in kwargs else args[1]
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
    hosts = Event.objects.filter(host=user)
    if hosts.exists():
      return HttpResponse(status=409)
    else:
      return function(*args, **kwargs)
  return wrapper
   
def InParty(function):
  def wrapper(*args, **kwargs):
    event_id = kwargs['event_id'] if 'event_id' in kwargs else args[1]
    request = args[0]
    user = getUserForTicket(request)
    event_goers = EventGoer.objects.filter(
      user=user, event__event_id__id=event_id)
    if len(event_goers) < 1:
      if FinishedEvent.objects.filter(event_id__id=event_id).exists():
        return HttpResponse(status=410) 
      else:
        return HttpResponseForbidden(
          "You must be logged into the party to do that")
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
    event = get_object_or_404(Event, event_id__id__exact=kwargs['event_id'])
    user = getUserForTicket(request)
    if event.host != user:
      return HttpResponseForbidden("Only the host may do that")
    else:
      return function(*args, **kwargs)
  return wrapper

def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if getDjangoTicketHeader() not in request.META:
      responseString = "Must provide the " + getTicketHeader() + " header. "
      return HttpResponseBadRequest(responseString)
    elif not isValidTicket(request.META[getDjangoTicketHeader()]):
      return HttpResponseForbidden("Invalid ticket")
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
    elif not isValidTicket(request.META[getDjangoTicketHeader()]):
      return HttpResponseForbidden("Invalid ticket")
    elif not ticketMatchesUser(request, user_id):
      return HttpResponseForbidden()
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
    
    
