from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import random
from models import Ticket
from datetime import datetime
from datetime import timedelta

def ticketMatchesUser(ticket_hash, provided_user_id):
  matchingTickets =  \
    Ticket.objects.filter(ticket_hash=provided_hash, user__id=provided_user_id)
  return len(matchingTickets) > 0
  

def isValidTicket(provided_hash):
  matchingTickets = Ticket.objects.filter(ticket_hash=provided_hash)
  if matchingTickets and  \
    (datetime.now() - matchingTickets[0].time_issued).days < 1:
    return True
  else:
    return False

def hasValidTicket(request):
  if not request.META.__contains__("udj_ticket_hash"):
    return False;
  else:
    return isValidTicket(request.META["udj_ticket_hash"])

def validAuthRequest(request):
  if not request.method == "POST":
    return False
  elif not request.POST.__contains__("username") \
    or not request.POST.__contains__("password"):
    return False
  return True
  

def generateRandomHash():
  rand_hash = random.getrandbits(128)
  toReturn = "%032x" % rand_hash
  return toReturn

def getUniqueRandHash():
  rand_hash = generateRandomHash()
  while Ticket.objects.filter(ticket_hash=rand_hash):
    rand_hash = generateRandomHash()
  return rand_hash


def getTicketForUser(userRequestingTicket):
  currentTickets = Ticket.objects.filter(user=userRequestingTicket)
  if currentTickets:
    for ticket in currentTickets:
      ticket.delete()
  toReturn = Ticket(user=userRequestingTicket, ticket_hash=getUniqueRandHash())
  toReturn.save()
  return toReturn 

@csrf_exempt
def authenticate(request):
  if not validAuthRequest(request):
    return HttpResponseBadRequest()

  userToAuth = get_object_or_404( \
    User, username__exact=request.POST["username"])
  if userToAuth.check_password(request.POST["password"]):
    ticket = getTicketForUser(userToAuth)
    response = HttpResponse()
    response['udj_ticket_hash'] = ticket.ticket_hash
    response['user_id'] = userToAuth.id
    return response
  else:
    print "bad username and password"
    return HttpResponseForbidden()
