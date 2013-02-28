import json
import hashlib
import random

from udj.models import Ticket
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import HasNZParams
from udj.views.views07.responses import HttpJSONResponse

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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
  return ticket


@csrf_exempt
@AcceptsMethods(['POST'])
@HasNZParams(['username', 'password'])
def authenticate(request):

  try:
    userToAuth = User.objects.get(username=request.POST['username'])
    if userToAuth.check_password(request.POST['password']):
      ticket = obtainTicketForUser(userToAuth)
      ticket_and_id = {"ticket_hash" : ticket.ticket_hash, "user_id" : str(userToAuth.id)}
      response = HttpJSONResponse(json.dumps(ticket_and_id))
      return response
  except ObjectDoesNotExist:
    pass

  response = HttpResponse(status=401)
  response['WWW-Authenticate'] = 'password'
  return response



