import json
import random

from udj.models import Ticket, FbUser
from udj.headers import DJANGO_TICKET_HEADER
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import HasNZJSONParams
from udj.views.views07.decorators import NeedsJSON
from udj.views.views07.responses import HttpJSONResponse, HttpResponseUnauthorized

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import uuid
import time
import hashlib


def generateRandomHash():
  """
  Thanks for the randoms murph!
  """
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


def generate_ticket_response(userToAuth):
  ticket = obtainNewTicketForUser(userToAuth)
  ticket_and_id = {"ticket_hash" : ticket.ticket_hash, "user_id" : str(userToAuth.id)}
  response = HttpJSONResponse(json.dumps(ticket_and_id))
  return response

@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsJSON
@HasNZJSONParams(['username', 'password'])
def authenticate(request, json_params):

  try:
    userToAuth = User.objects.get(username=json_params['username'])
    if userToAuth.has_usable_password() and userToAuth.check_password(json_params['password']):
      return generate_ticket_response(userToAuth)
  except ObjectDoesNotExist:
    pass

  return HttpResponseUnauthorized('password')


@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsJSON
@HasNZJSONParams(['user_id', 'access_token'])
def fb_authenticate(request, json_params):
  import requests
  params = {
      "fields" : "last_name,first_name,email,username",
      "access_token" : json_params['access_token']
  }

  url = "https://graph.facebook.com/{0}".format(json_params['user_id'])
  user_request = requests.get(url, params=params)
  user_data = json.loads(user_request.text)

  if ("last_name" not in user_data or
      "first_name" not in user_data or
      "email" not in user_data or
      "username" not in user_data):
    return HttpResponseUnauthorized('access-token')

  user_to_auth = None
  try:
    user_to_auth = FbUser.objects.get(fb_user_id=json_params['user_id']).user
  except ObjectDoesNotExist:
    user_to_auth = User(username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'])
    user_to_auth.set_unusable_password()
    user_to_auth.save()
    FbUser(user=user_to_auth, fb_user_id=json_params['user_id']).save()

  return generate_ticket_response(user_to_auth)


