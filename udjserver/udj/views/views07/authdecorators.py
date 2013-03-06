from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.headers import TICKET_HEADER

from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from udj.views.views07.responses import HttpResponseForbiddenWithReason


"""
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
"""


def HasPlayerPermissions(required_permissions, player_arg_position=1):
  def decorator(target):
    def wrapper(*args, **kwargs):
      request = args[0]
      try:
        player = args[player_arg_position]
      except IndexError:
        player = kwargs['player']
      for perm in required_permissions:
        if not player.user_has_permission(perm, request.udjuser):
          return HttpResponseForbiddenWithReason('player-permission')
      return target(*args, **kwargs)
    return wrapper
  return decorator

def IsntOwner(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = request.udjuser
    player = kwargs['player']
    if player.owning_user==user:
      return HttpResponseBadRequest()
    else:
      return function(*args, **kwargs)
  return wrapper


def IsOwnerOrParticipates(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = request.udjuser
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

"""
def IsOwner(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = request.udjuser
    activePlayer = kwargs['activePlayer']
    if activePlayer.owning_user==user:
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper

"""

def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if DJANGO_TICKET_HEADER not in request.META:
      responseString = "Must provide the " + TICKET_HEADER + " header. "
      toReturn = HttpResponse(responseString, status=401)
      toReturn['WWW-Authenticate'] = 'ticket-hash'
      return toReturn

    try:
      validticket = Ticket.objects.get(ticket_hash=request.META[DJANGO_TICKET_HEADER])
      args[0].udjuser = validticket.user
      return function(*args, **kwargs)
    except ObjectDoesNotExist:
      toReturn = HttpResponse("Invalid ticket: \"" + 
        request.META[DJANGO_TICKET_HEADER] + "\"", status=401)
      toReturn['WWW-Authenticate'] = 'ticket-hash'
      return toReturn
  return wrapper

"""
def IsOwnerOrAdmin(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = request.udjuser
    player = kwargs['player']
    if player.owning_user==user or player.isAdmin(user):
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper

def IsOwnerOrParticipatingAdmin(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = request.udjuser
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
    user = request.udjuser
    player = kwargs['player']
    if player.canCreateSongSets(user):
      return function(*args, **kwargs)
    else:
      return HttpResponseForbidden()
  return wrapper

"""

