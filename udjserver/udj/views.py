# Create your views here.
import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import LibraryEntryEncoder
from udj.JSONCodecs import getLibraryEntryFromJSON
from udj.models import LibraryEntry

def addSongToLibrary(songJson, user_id):
  toInsert = getLibraryEntryFromJSON(songJson, user_id)
  toInsert.save()
  return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
def addSongsToLibrary(request, user_id):

  payload = request.raw_post_data
  #TODO catch any exception in the json parsing and return a bad request
  convertedPayload = json.loads(payload)

  addedSongs = []
  for libEntry in convertedPayload:
    addedSongs.append(addSongToLibrary(libEntry, user_id))
  data = json.dumps(addedSongs, cls=LibraryEntryEncoder)

  return HttpResponse(data, status=201)

@AcceptsMethods('DELETE')
@TicketUserMatch
def deleteSongFromLibrary(request, user_id, lib_id):
  matchedEntries = LibraryEntry.objects.filter(
    server_lib_song_id=lib_id, owning_user=user_id
  )
  if len(matchedEntries) != 1:
    return HttpResponseNotFound()
  matchedEntries[0].delete()
  return HttpResponse("Deleted item: " + lib_id)

@AcceptsMethods('DELETE')
@TicketUserMatch
def deleteEntireLibrary(request, user_id):
  LibraryEntry.objects.filter(user_id=user_id).delete()
  return HttpResponse("Deleted all items from the library")
