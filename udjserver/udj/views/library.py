# Create your views here.
import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import getLibraryEntryFromJSON
from udj.models import LibraryEntry

def addSongToLibrary(songJson, user_id):
  preivouslyAdded = LibraryEntry.objects.filter(
    host_lib_song_id=songJson['id'], 
    owning_user__id=user_id)
  if preivouslyAdded.exists():
    return preivouslyAdded[0]
  else:
    toInsert = getLibraryEntryFromJSON(songJson, user_id)
    toInsert.save()
    return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
def addSongsToLibrary(request, user_id):

  #TODO catch any exception in the json parsing and return a bad request
  songsToAdd = json.loads(request.raw_post_data)

  toReturn = []
  for libEntry in songsToAdd:
    addedSong = addSongToLibrary(libEntry, user_id)
    toReturn.append(addedSong.host_lib_song_id)

  return HttpResponse(json.dumps(toReturn), status=201)

@AcceptsMethods('DELETE')
@TicketUserMatch
def deleteSongFromLibrary(request, user_id, lib_id):
  try:
    LibraryEntry.objects.get(
      host_lib_song_id=lib_id, 
      owning_user=user_id).delete()
  except DoesNotExist:
    return HttpResponseNotFound()
  return HttpResponse("Deleted item: " + lib_id)

@AcceptsMethods('DELETE')
@TicketUserMatch
def deleteEntireLibrary(request, user_id):
  LibraryEntry.objects.filter(owning_user__id=user_id).delete()
  return HttpResponse("Deleted all items from the library")
