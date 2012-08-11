from udj.models import Participant
from udj.views.views06.auth import isValidTicket
from udj.views.views06.auth import ticketMatchesUser
from udj.views.views06.auth import getUserForTicket
from udj.headers import DJANGO_TICKET_HEADER
from udj.headers import TICKET_HEADER

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden

def IsntOwner(function)
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if player.owning_user==user:
      return HttpResponseBadRequest()
    else:
      return function(*args, **kwargs)
  return wrapper

def IsOwnerOrParticipates(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if player.owning_user==user or player.isActiveParticipant(user):
      return function(*args, **kwargs)
    elif player.isKicked(user):
      toReturn = HttpResponse(status=401)
      toReturn['WWW-Authenticate'] = 'kicked'
      return toReturn
    else:
      toReturn = HttpResponse(status=401)
      toReturn['WWW-Authenticate'] = 'begin-participating'
      return toReturn
  return wrapper

def IsOwner(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    activePlayer = kwargs['activePlayer']
    if activePlayer.owning_user==user:
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper


def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if DJANGO_TICKET_HEADER not in request.META:
      responseString = "Must provide the " + TICKET_HEADER + " header. "
      toReturn = HttpResponse(responseString, status=401)
      toReturn['WWW-Authenticate'] = 'ticket-hash'
      return toReturn
    elif not isValidTicket(request.META[DJANGO_TICKET_HEADER]):
      toReturn = HttpResponse("Invalid ticket: \"" + 
        request.META[DJANGO_TICKET_HEADER] + "\"", status=401)
      toReturn['WWW-Authenticate'] = 'ticket-hash'
      return toReturn
    else:
      return function(*args, **kwargs)
  return wrapper

def IsOwnerOrAdmin(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if player.owning_user==user or player.isAdmin(user):
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper

def IsOwnerOrParticipatingAdmin(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if player.owning_user==user:
      return function(*args, **kwargs)
    elif player.isAdmin(user):
      if player.isActiveParticipant(user):
        return function(*args, **kwargs)
      else:
        toReturn = HttpResponse(status=401)
        toReturn['WWW-Authenticate'] = 'begin-participating'
        return toReturn
    else:
      return HttpResponseForbidden()
  return wrapper


def CanCreateSongSets(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if player.canCreateSongSets(user):
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper


