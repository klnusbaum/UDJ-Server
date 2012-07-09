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

def PlayerExists(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    player_id = kwargs['player_id']
    try:
      actualPlayer = Player.objects.get(pk=player_id)
      kwargs['player'] = actualPlayer
      return function(*args, **kwargs)
    except ObjectDoesNotExist:
      toReturn =  HttpResponseNotFound()
      toReturn[MISSING_RESOURCE_HEADER] = 'player'
      return toReturn
  return wrapper

def ActivePlayerExists(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    player_id = kwargs['player_id']
    try:
      potentialPlayer = Player.objects.get(id=player_id)
      if potentialPlayer.state != 'IN':
        kwargs['activePlayer'] = potentialPlayer
        return function(*args, **kwargs)
      else:
        toReturn =  HttpResponseNotFound("Player inactive")
        toReturn[MISSING_RESOURCE_HEADER] = 'player'
        toReturn[MISSING_REASON_HEADER] = 'inactive'
        return toReturn
    except ObjectDoesNotExist:
      toReturn =  HttpResponseNotFound()
      toReturn[MISSING_RESOURCE_HEADER] = 'player'
      return toReturn
  return wrapper

def UpdatePlayerActivity(function):
  def wrapper(*args, **kwargs):
    user = kwargs['user']
    activePlayer = kwargs['activePlayer']
    if user != activePlayer.owning_user:
      participant = Participant.objects.get(user=user, player=activePlayer)
      participant.time_last_interaction = datetime.now()
      participant.save()
    return function(*args, **kwargs)
  return wrapper

