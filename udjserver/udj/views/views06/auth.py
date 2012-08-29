import json
import hashlib
import random
from datetime import datetime

from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.helpers import HttpJSONResponse

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from settings import TICKET_EXPIRATION_LENGTH

def hashPlayerPassword(password):
  m = hashlib.sha1()
  m.update(password)
  return m.hexdigest()


def getUserForTicket(request):
  return Ticket.objects.get(
    ticket_hash=request.META[DJANGO_TICKET_HEADER]).user

def ticketMatchesUser(request, provided_user_id):
  try:
    matchingTickets = Ticket.objects.get(
      ticket_hash=request.META[DJANGO_TICKET_HEADER],
      user__id=provided_user_id)
  except ObjectDoesNotExist:
    return False
  return True

def isValidTicket(provided_hash):
  try:
    matchingTicket = Ticket.objects.get(ticket_hash=provided_hash)
  except ObjectDoesNotExist:
    return False
  if(datetime.now() - matchingTicket.time_issued).days < TICKET_EXPIRATION_LENGTH:
    return True
  else:
    return False

def generateRandomHash():
  rand_hash = random.getrandbits(128)
  toReturn = "%032x" % rand_hash
  return toReturn

def getUniqueRandHash():
  rand_hash = generateRandomHash()
  while Ticket.objects.filter(ticket_hash=rand_hash).exists():
    rand_hash = generateRandomHash()
  return rand_hash


def obtainTicketForUser(userRequestingTicket):
  ticket , created = Ticket.objects.get_or_create(
    user=userRequestingTicket,
    defaults={'ticket_hash' : getUniqueRandHash()})

  if not created and (datetime.now() - ticket.time_issued).days >= 1:
    ticket.ticket_hash=getUniqueRandHash()
    ticket.time_issued=datetime.now()
    ticket.save()
  return ticket


@csrf_exempt
@AcceptsMethods(['POST'])
@HasNZParams(['username', 'password'])
def authenticate(request):

  try:
    userToAuth = User.objects.get(username=request.POST['username'])
    if userToAuth.check_password(request.POST['password']):
      ticket = obtainTicketForUser(userToAuth)
      ticket_and_id = {"ticket_hash" : ticket.ticket_hash, "user_id" : userToAuth.id}
      response = HttpJSONResponse(json.dumps(ticket_and_id))
      return response
    else:
      response = HttpResponse(status=401)
      response['WWW-Authenticate'] = 'password'
      return response
  except ObjectDoesNotExist:
    response = HttpResponse(status=401)
    response['WWW-Authenticate'] = 'password'
    return response



