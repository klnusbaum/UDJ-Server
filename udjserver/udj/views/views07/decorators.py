from udj.headers import DJANGO_TICKET_HEADER
from udj.headers import MISSING_RESOURCE_HEADER
from udj.headers import MISSING_REASON_HEADER
from udj.models import Player
from udj.models import Participant

from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime


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


def HasNZParams(necessaryParams):
  def decorator(target):
    def wrapper(*args, **kwargs):
      request = args[0]
      for param in necessaryParams:
        if not (param in request.REQUEST) or request.REQUEST[param] == "":
          return HttpResponseBadRequest("Must include non-blank " + param + " parameter")
      return target(*args, **kwargs)
    return wrapper
  return decorator

def NeedsJSON(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if not request.META.has_key('CONTENT_TYPE'):
      return HttpResponseBadRequest("must specify content type")
    elif request.META['CONTENT_TYPE'] != 'text/json':
      return HttpResponse("must send json", status=415)
    elif request.raw_post_data == '':
      return HttpResponseBadRequest("Bad JSON")
    else:
      return function(*args, **kwargs)
  return wrapper

"""
def PlayerExists(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    try:
      actualPlayer = Player.objects.get(pk=kwargs['player_id'])
      kwargs['player'] = actualPlayer
      return function(*args, **kwargs)
    except ObjectDoesNotExist:
      toReturn = HttpResponseNotFound()
      toReturn[MISSING_RESOURCE_HEADER] = 'player'
      return toReturn
  return wrapper

def PlayerIsActive(function):
  def wrapper(*args, **kwargs):
    if 'player' in kwargs:
      player = kwargs['player']
    else:
      #This is a kludge for when player is actually an arg and not a kwarg
      player = args[2]
    if player.state == u'IN':
      toReturn =  HttpResponseNotFound()
      toReturn[MISSING_RESOURCE_HEADER] = 'player'
      toReturn[MISSING_REASON_HEADER] = 'inactive'
      return toReturn
    else:
      return function(*args, **kwargs)
  return wrapper


def UpdatePlayerActivity(function):
  from udj.views.views06.auth import getUserForTicket
  def wrapper(*args, **kwargs):
    toReturn = function(*args, **kwargs)
    request = args[0]
    user = getUserForTicket(request)
    player = kwargs['player']
    if user != player.owning_user:
      participant = Participant.objects.get(user=user, player=player)
      participant.time_last_interaction = datetime.now()
      participant.save()
    return toReturn
  return wrapper

"""
