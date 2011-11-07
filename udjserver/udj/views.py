# Create your views here.
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from myauth import hasValidTicket
from myauth import ticketMatchesUser
from django import serializers

def addSongs(request, user_id):
  if not hasValidTicket(request) or \
  not ticketMatchesUser(request.META["udj_ticket_hash"], user_id):
    return HttpResponseForbidden()
  payload = request.readlines()
  for song in serializers.deserialize("json", payload):
    del song['server_lib_song_id']
    song.save()
