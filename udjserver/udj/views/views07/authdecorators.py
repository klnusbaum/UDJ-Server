from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.headers import TICKET_HEADER
from udj.views.views07.responses import HttpResponseForbiddenWithReason, HttpResponseUnathorized

from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from datetime import datetime

from settings import TICKET_VALIDITY_LENGTH


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
      return HttpResponseUnathorized('kicked')
    else:
      return HttpResponseUnathorized('begin-participating')
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
      return HttpResponseUnathorized('ticket-hash')

    try:
      validticket = Ticket.objects.get(ticket_hash=request.META[DJANGO_TICKET_HEADER],
                                       time_last_used__gte=datetime.now()-TICKET_VALIDITY_LENGTH)
      validticket.time_last_used = datetime.now()
      validticket.save()
      args[0].udjuser = validticket.user
      return function(*args, **kwargs)
    except ObjectDoesNotExist:
      return HttpResponseUnathorized('ticket-hash')
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

