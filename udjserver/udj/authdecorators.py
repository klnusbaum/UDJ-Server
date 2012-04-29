from udj.models import Participant
from udj.auth import isValidTicket
from udj.auth import ticketMatchesUser
from udj.auth import getUserForTicket
from udj.headers import DJANGO_TICKET_HEADER
from udj.headers import TICKET_HEADER

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden



def userParticipates(player, user):
  return Participant.objects.filter(user=user).exists()

def IsOwnerOrParticipates(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user = getUserForTicket(request)
    activePlayer = kwargs['activePlayer']
    if activePlayer.owning_user==user or userParticipates(activePlayer, user):
      kwargs['user'] = user
      return function(*args, **kwargs)
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
      return HttpResponseBadRequest(responseString)
    elif not isValidTicket(request.META[DJANGO_TICKET_HEADER]):
      return HttpResponseForbidden("Invalid ticket: \"" + 
        request.META[DJANGO_TICKET_HEADER] + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    if not ticketMatchesUser(request, user_id):
      return HttpResponseForbidden("The ticket doesn't match the given user\n" +
        "Given Ticket: \"" + request.META[DJANGO_TICKET_HEADER] + "\"\n" +
        "Given User id: \"" + user_id + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper
