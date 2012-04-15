import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import random
from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.decorators import AcceptsMethods
from udj.decorators import HasNZParams
from datetime import datetime

def getUserForTicket(request):
  return Ticket.objects.get(
    ticket_hash=request.META[DJANGO_TICKET_HEADER]).user

def ticketMatchesUser(request, provided_user_id):
  matchingTickets = Ticket.objects.filter(
    ticket_hash=request.META[DJANGO_TICKET_HEADER],
    user__id=provided_user_id)
  return len(matchingTickets) > 0

def isValidTicket(provided_hash, ip_address, port):
  try:
    matchingTicket = Ticket.objects.get(ticket_hash=provided_hash,
      source_ip_addr=ip_address, source_port=port)
  except ObjectDoesNotExist:
    return False
  if(datetime.now() - matchingTicket.time_issued).days < 1:
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


def obtainTicketForUser(userRequestingTicket, givenIpAddress, givenPort):
  ticket , created = Ticket.objects.get_or_create(
    user=userRequestingTicket,
    source_ip_addr=givenIpAddress,
    source_port=givenPort)
  defaults={'ticket_hash' : getUniqueRandHash()}
  if not created:
    ticket.ticket_hash=getUniqueRandHash()
    ticket.save()
  return ticket


@csrf_exempt
@AcceptsMethods(['POST'])
@HasNZParams(['username', 'password'])
def authenticate(request):
  if request.method != 'POST':
    return HttpResponse('Must send post', status=405)
  elif not request.POST.__contains__("username"):
    return HttpResponseBadRequest('Must send username')
  elif not request.POST.__contains__("password"):
    return HttpResponseBadRequest('Must send password')


  userToAuth = get_object_or_404(User, username=request.POST['username'])
  if userToAuth.check_password(request.POST['password']):
    ticket = obtainTicketForUser(
        userToAuth, request.META['REMOTE_ADDR'], request.META['REMOTE_PORT'])
    ticket_and_id = {"ticket_hash" : ticket.ticket_hash, "user_id" : userToAuth.id}
    response = HttpResponse(json.dumps(ticket_and_id), content_type='text/json')
    return response
  else:
    response = HttpResponse(status=401)
    response['WWW-Authenticate'] = 'password'
    return response

