# Create your views here.
import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from myauth import hasValidTicket
from myauth import ticketMatchesUser
from myauth import getInvalidTicketResponse
from django.core import serializers
from django.contrib.auth.models import User
from udj.models import LibraryEntry


def addSongs(request, user_id):
  if request.method != 'PUT':
    return HttpResponseNotAllowed()

  if not hasValidTicket(request):
    return getInvalidTicketResponse(request)

  if not ticketMatchesUser(request.META["udj_ticket_hash"], user_id):
    toReturn = HttpResponseForbidden()
    toReturn['error'] = "ticket didn't match user"
    return toReturn
   
  payload = request.raw_post_data
  
  if payload == "":
    return HttpResponseBadRequest()
   
  convertedPayload = json.loads(payload)

  for libEntry in convertedPayload:
    toInsert = LibraryEntry( \
      host_lib_song_id = int(libEntry['host_lib_song_id']), \
      song = libEntry['song'], \
      artist  = libEntry['artist'], \
      album = libEntry['album'], \
      owning_user = User.objects.filter(id=user_id)[0])
    toInsert.save()
  return HttpResponse('ok', status=200)
