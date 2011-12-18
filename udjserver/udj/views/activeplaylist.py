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

def hasBeenAdded(song, event_id, user):

  return \
    ActivePlaylistEntry.objects.filter(
      adder=user, 
      client_request_id=song['client_request_id'],
      event__event_id__id=event_id
    ).exists() \
  or \
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
    ).exists() \
  or \
    DeletedPlaylistEntry.objects.filter(
      event__event_id__id=event_id,
      adder=user, 
      client_request_id=song['client_request_id']
    ).exists()

  
def addSong2ActivePlaylist(song, event_id, adding_user):
  print "in adding song to active playlist"
  added = ActivePlaylistEntry(
    song=LibraryEntry.objects.get(pk=song['lib_id']),
    adder=adding_user,
    event=Event.objects.get(event_id__id=event_id),
    client_request_id=song['client_request_id'])
  print "before save"
  added.save()
  print "after save"
  UpVote(playlist_entry=added, user=adding_user).save()
  print "after upvote"

#TODO Need to add a check to make sure that they aren't trying to add
#a song  that's not in the available music.
@NeedsAuth
@InParty
@AcceptsMethods('PUT')
@NeedsJSON
def addToPlaylist(request, event_id):
  user = getUserForTicket(request)
  songsToAdd = json.loads(request.raw_post_data)
  for song in songsToAdd:
    if not hasBeenAdded(song, event_id, user):
      addSong2ActivePlaylist(song, event_id, user)
  
  return HttpResponse(status = 201)

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
