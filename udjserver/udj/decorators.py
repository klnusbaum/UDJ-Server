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
    request = args[0]
    user = getUserForTicket(request)
    event = get_object_or_404(Event, id__exact=kwargs['event_id'])
    event_goers = EventGoer.objects.filter(user=user, event=event)
    if len(event_goers) != 1:
      return HttpResponseForbidden()
    else:
      return function(*args, **kwargs)
  return wrapper

def IsUserOrHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    event = get_object_or_404(Event, id__exact=kwargs['event_id'])
    user = getUserForTicket(request)
    if event.host == user or user.id == int(kwargs['user_id']):
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper

#TODO actually implement this fucntion. i.e. check for password compliance
def CanLoginToEvent(function):
  def wrapper(*args, **kwargs):
    return function(*args, **kwargs)
  return wrapper


def EventExists(function):
  def wrapper(*args, **kwargs):
    event = get_object_or_404(Event, id__exact=kwargs['event_id'])
    return function(*args, **kwargs)
  return wrapper

def IsEventHost(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    event = get_object_or_404(Event, id__exact=kwargs['event_id'])
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
    
    
