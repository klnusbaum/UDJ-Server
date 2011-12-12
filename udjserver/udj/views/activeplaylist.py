import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from udj.decorators import IsEventHost
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
from udj.models import DeletedPlaylistEntry
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
  playlistEntries = ActivePlaylistEntry.objects.filter(event__event_id__id=event_id).\
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
      event__event_id__id=event_id, 
      adder=user, 
      client_request_id=song['client_request_id']
    ).exists() \
    or \
    PlayedPlaylistEntry.objects.filter(
      event__event_id__id=event_id,
      adder=user, 
      client_request_id=song['client_request_id']
    )
  
def addSong2ActivePlaylist(song, event_id, adding_user):
  toReturn = ActivePlaylistEntry(
    song=LibraryEntry.objects.get(pk=song['lib_id']),
    adder=adding_user,
    event=Event.objects.get(event_id__id=event_id),
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
      event__event_id__id=event_id)

    #If the song is already in the queue
    if inQueue.exists():
      addedSong = inQueue[0]
      upvotes = UpVote.objects.filter(playlist_entry=addedSong).count()
      downvotes = DownVote.objects.filter(playlist_entry=addedSong).count()
      toReturn['added_entries'].append(
        getActivePlaylistEntryDictionary(addedSong, upvotes, downvotes))
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
  
  return HttpResponse(json.dumps(toReturn), status = 201)

@NeedsAuth
@InParty
@AcceptsMethods('POST')
def voteSongDown(request, event_id, playlist_id):
  return voteSong(request, event_id, playlist_id, DownVote)

@NeedsAuth
@InParty
@AcceptsMethods('POST')
def voteSongUp(request, event_id, playlist_id):
  return voteSong(request, event_id, playlist_id, UpVote)



def hasAlreadyVoted(votingUser, entryToVote, VoteType):
  return VoteType.objects.filter(
    user=votingUser, playlist_entry=entryToVote).exists()

def voteSong(request, event_id, playlist_id, VoteType):
  votingUser = getUserForTicket(request)
  entryToVote = get_object_or_404(ActivePlaylistEntry, pk=playlist_id)
  if hasAlreadyVoted(votingUser, entryToVote, VoteType):
    return HttpResponseForbidden()

  VoteType(playlist_entry=entryToVote, user=votingUser).save()
  return HttpResponse()

@NeedsAuth
@IsEventHost
@AcceptsMethods('DELETE')
def removeSongFromActivePlaylist(request, event_id, playlist_id):
  if DeletedPlaylistEntry.objects.filter(original_id=playlist_id, 
    event__id=event_id):
    return HttpResponse()

  toRemove = get_object_or_404(
    ActivePlaylistEntry, pk=playlist_id, event__id=event_id)
  DeletedPlaylistEntry(original_id=playlist_id, adder=toRemove.adder,
    event=toRemove.event, client_request_id=toRemove.client_request_id).save()
  toRemove.delete()
  return HttpResponse()
