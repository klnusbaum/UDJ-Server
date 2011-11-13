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

def addSongToLibrary(songJson, user_id, host_lib_id):
  toInsert = getLibraryEntryFromJSON(songJson, user_id, host_lib_id)
  toInsert.save()
  return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
def addSongsToLibrary(request, user_id):

  payload = request.raw_post_data
  #TODO catch any exception in the json parsing and return a bad request
  jsonPayload = json.loads(payload)
  songsToAdd = jsonPayload["to_add"]
  idMaps = jsonPayload["id_maps"]

  counter = 0
  for libEntry in songsToAdd:
    addedSong = \
      addSongToLibrary(libEntry, user_id, idMaps[counter]["client_id"])
    idMaps[counter]["server_id"] = addedSong.server_lib_song_id
    counter = counter +1
  toReturn = json.dumps(idMaps)

  return HttpResponse(toReturn, status=201)

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
  LibraryEntry.objects.filter(owning_user__id=user_id).delete()
  return HttpResponse("Deleted all items from the library")
