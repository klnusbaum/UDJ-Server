import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.JSONCodecs import getPlaylistFromJSON
from udj.JSONCodecs import getPlaylistEntryFromJSON
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
    addedPlaylist = addPlaylist(playlist, user_id, idMaps[counter]["client_id"])
    idMaps[counter]["server_id"] = addedPlaylist.server_playlist_id
    counter = counter +1
  toReturn = json.dumps(idMaps)

  return HttpResponse(toReturn, status=201)

@AcceptsMethods('DELETE')
@TicketUserMatch
def deletePlaylist(request, user_id, playlist_id):
  matchedEntries = Playlist.objects.filter(
    server_playlist_id=playlist_id,
    owning_user=user_id)
  if len(matchedEntries) != 1:
    return HttpResponseNotFound()
  matchedEntries[0].delete()
  return HttpResponse("Deleted playlist: " + playlist_id)

def addSongToPlaylist(song_id, playlist_id, user_id, host_id):
  toInsert = getPlaylistEntryFromJSON(song_id, playlist_id, user_id, host_id)
  toInsert.save()
  return toInsert

@AcceptsMethods('PUT')
@NeedsJSON
@TicketUserMatch
def addPlaylistEntries(request, user_id, playlist_id):
  payload = json.loads(request.raw_post_data)
  songsToAdd = payload["to_add"]
  idMaps = payload["id_maps"]

  counter = 0
  for song_id in songsToAdd:
    addedSong = addSongToPlaylist(
      song_id, playlist_id, user_id, idMaps[counter]["client_id"])
    idMaps[counter]["server_id"] = addedSong.server_playlist_entry_id
    counter = counter +1
  toReturn = json.dumps(idMaps)

  return HttpResponse(toReturn, status=201)
  
