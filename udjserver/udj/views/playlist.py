import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import getPlaylistFromJSON
from udj.models import Playlist
from udj.models import PlaylistEntry

def addPlaylist(playlistJson, user_id, host_id):
  toInsert = getPlaylistFromJSON(playlistJson, user_id, host_id)
  toInsert.save()
  return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
def addPlaylists(request, user_id):
  payload = json.loads(request.raw_post_data)
  playlistsToAdd = payload["to_add"]
  idMaps = payload["id_maps"]

  counter = 0
  for playlist in playlistsToAdd:
    addedPlaylist = \
      addPlaylist(playlist, user_id, idMaps[counter]["client_id"])
    idMaps[counter]["server_id"] = addedPlaylist.server_playlist_id
    counter = counter +1
  toReturn = json.dumps(idMaps)

  return HttpResponse(toReturn, status=201)
