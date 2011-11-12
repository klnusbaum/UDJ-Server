# Create your views here.
import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.core import serializers
from django.contrib.auth.models import User
from udj.models import LibraryEntry
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON

def addSong(songJson, user_id):
  toInsert = LibraryEntry( \
    host_lib_song_id = int(songJson['host_lib_song_id']), \
    song = songJson['song'], \
    artist  = songJson['artist'], \
    album = songJson['album'], \
    owning_user = User.objects.filter(id=user_id)[0])
  toInsert.save()
  return toInsert


@AcceptsMethods({'PUT'})
@NeedsJSON
@TicketUserMatch
def addSongs(request, user_id):

  payload = request.raw_post_data
  
  """
  if payload == "":
    return HttpResponseBadRequest()
  """
   
  #TODO catch any exception in the json parsing and return a bad request
  convertedPayload = json.loads(payload)

  addedSongs = []
  for libEntry in convertedPayload:
    addedSongs.append(addSong(libEntry, user_id))

  data = serializers.serialize("json", addedSongs)

  return HttpResponse(data)
