# Create your views here.
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from myauth import hasValidTicket
from myauth import ticketMatchesUser
from django.core import serializers
from django.contrib.auth.models import User

def addSongs(request, user_id):
  if not hasValidTicket(request):
    toReturn = HttpResponseForbidden()
    toReturn['error'] = "invalid ticket" + ticket_validity
    return toReturn

  if not ticketMatchesUser(request.META["HTTP_UDJ_TICKET_HASH"], user_id):
    toReturn = HttpResponseForbidden()
    toReturn['error'] = "ticket didn't match user"
    return toReturn
   
  payload = request.readlines()
  #print "Payload \n %s" % payload
  for song in serializers.deserialize("json", payload):
    del song['server_lib_song_id']
    song['owning_user'] = User.objects.filter(id=user_id)[0]
    song.save()

def default(request):
  return HttpResponse("You should chekcout www.zombo.com")
