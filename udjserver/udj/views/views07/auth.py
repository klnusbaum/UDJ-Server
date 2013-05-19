import json
import random

from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import HasNZJSONParams
from udj.views.views07.decorators import NeedsJSON
from udj.views.views07.responses import HttpJSONResponse

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import uuid
import time
import hashlib


def generateRandomHash():
  rand = uuid.uuid4()
  seconds = int(time.time())
  raw = "UDJ-{0!s}-{1!s}".format(rand, seconds)
  return hashlib.sha256(raw).hexdigest()

def obtainNewTicketForUser(userRequestingTicket):
  """
  There is a non-zero probability that we may get a unqiueness violation here
  by generating the same random hash. However, the probability of this is so
  astronomically small, we choose to not account for it. Google it if you don't
  beleive me.
  """
  ticket = Ticket(user=userRequestingTicket, ticket_hash=generateRandomHash())
  ticket.save()
  return ticket


@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsJSON
@HasNZJSONParams(['username', 'password'])
def authenticate(request, json_params):

  try:
    userToAuth = User.objects.get(username=json_params['username'])
    if userToAuth.check_password(json_params['password']):
      ticket = obtainNewTicketForUser(userToAuth)
      ticket_and_id = {"ticket_hash" : ticket.ticket_hash, "user_id" : str(userToAuth.id)}
      response = HttpJSONResponse(json.dumps(ticket_and_id))
      return response
  except ObjectDoesNotExist:
    pass

  response = HttpResponse(status=401)
  response['WWW-Authenticate'] = 'password'
  return response



