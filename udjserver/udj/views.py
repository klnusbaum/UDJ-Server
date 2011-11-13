# Create your views here.
import json
from django.http import HttpRequest
from django.http import HttpResponse
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import LibraryEntryEncoder
from udj.JSONCodecs import getLibraryEntryFromJSON

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

  return HttpResponse(data)
