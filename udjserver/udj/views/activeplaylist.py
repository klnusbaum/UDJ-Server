import json
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import InParty
from udj.models import ActivePlaylistEntry
from udj.models import LibraryEntry
from udj.models import Event
from udj.models import CurrentSong
from udj.models import UpVote
from udj.models import DownVote
from udj.models import PlayedPlaylistEntry
from udj.JSONCodecs import getJSONForActivePlaylistEntries
from udj.JSONCodecs import getActivePlaylistEntryDictionary
from udj.auth import getUserForTicket

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getActivePlaylist(request, event_id):
  """
  My guess is that if you help write the software for DMBSes, this query is
  going to make your cry. My sincerest apologies.
  """
  playlistEntries = ActivePlaylistEntry.objects.filter(event__id=event_id).\
    extra(
      select={
        'upvotes' : 'SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.id',

        'downvotes' : 'select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.id',
        'total_votes' : '(SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.id)-' +\
        '(select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.id)'
      },
      order_by = ['-total_votes', 'time_added'])
    
  return HttpResponse(getJSONForActivePlaylistEntries(playlistEntries))

def hasBeenPlayed(song, event_id, user):
  return \
    CurrentSong.objects.filter(
      event__id=event_id, 
      adder=user, 
      client_request_id=song['client_request_id']
    ).exists() \
    or \
    PlayedPlaylistEntry.objects.filter(
      event__id=event_id,
      adder=user, 
      client_request_id=song['client_request_id']
    )
  
def addSong2ActivePlaylist(song, event_id, adding_user):
  toReturn = ActivePlaylistEntry(
    song=LibraryEntry.objects.get(pk=song['lib_id']),
    adder=adding_user,
    event=Event.objects.get(pk=event_id),
    client_request_id=song['client_request_id'])
  toReturn.save()
  UpVote(playlist_entry=toReturn, user=adding_user).save()
  return toReturn

#TODO Need to add a check to make sure that they aren't trying to add
#a song  that's not in the available music.
@NeedsAuth
@InParty
@AcceptsMethods('PUT')
@NeedsJSON
def addToPlaylist(request, event_id):
  user = getUserForTicket(request)
  songsToAdd = json.loads(request.raw_post_data)
  toReturn = { 'added_entries' : [], 'request_ids' : [], 'already_played' : [] }
  for song in songsToAdd:
    inQueue = ActivePlaylistEntry.objects.filter(
      adder=user, 
      client_request_id=song['client_request_id'],
      event__id=event_id)

    #If the song is already in the queue
    if inQueue.exists():
      addedSong = inQueue[0]
      upvotes = UpVote.objects.filter(playlist_entry=addedSong).count()
      downvotes = DownVote.objects.filter(playlist_entry=addedSong).count()
      toReturn['added_entries'].append(
        getActivePlaylistEntryDictionary(inQueue, upvotes, downvotes))
      toReturn['request_ids'].append(song['client_request_id'])

    #If the song has already been played
    elif hasBeenPlayed(song, event_id, user):
      toReturn['already_played'].append(song['client_request_id'])

    #If we actually need to add the song
    else:
      addedSong = addSong2ActivePlaylist(song, event_id, user)
      toReturn['added_entries'].append(
        getActivePlaylistEntryDictionary(addedSong, 1, 0))
      toReturn['request_ids'].append(song['client_request_id'])
  
  return HttpResponse(json.dumps(toReturn))
