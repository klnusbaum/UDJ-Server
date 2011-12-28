import json
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from udj.decorators import IsEventHost
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import InParty
from udj.decorators import TicketUserMatch
from udj.models import ActivePlaylistEntry
from udj.models import LibraryEntry
from udj.models import Event
from udj.models import UpVote
from udj.models import DownVote
from udj.JSONCodecs import getJSONForActivePlaylistEntries
from udj.auth import getUserForTicket

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getActivePlaylist(request, event_id):
  """
  My guess is that if you help write the software for DMBSes, this query is
  going to make your cry. My sincerest apologies.
  """
  playlistEntries = ActivePlaylistEntry.objects.filter(
    event__id=event_id, state=u'QE').\
    extra(
      select={
        'upvotes' : 'SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = id',

        'downvotes' : 'select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = id',
        'total_votes' : '(SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = id)-' +\
        '(select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = id)'
      },
      order_by = ['-total_votes', 'time_added'])
    
  return HttpResponse(getJSONForActivePlaylistEntries(playlistEntries))

def hasBeenAdded(song_request, event_id, user):
  return ActivePlaylistEntry.objects.filter(
      adder=user, 
      client_request_id=song_request['client_request_id'],
      event__id=event_id
    ).exists() 

  
def addSong2ActivePlaylist(song_request, event_id, adding_user):
  event = Event.objects.get(pk=event_id)
  songToAdd = LibraryEntry.objects.get(
      host_lib_song_id=song_request['lib_id'], owning_user=event.host)
  added = ActivePlaylistEntry(
    song=songToAdd,
    adder=adding_user,
    event=event,
    client_request_id=song_request['client_request_id'])
  added.save()
  UpVote(playlist_entry=added, user=adding_user).save()

#TODO Need to add a check to make sure that they aren't trying to add
#a song  that's not in the available music.
@NeedsAuth
@InParty
@AcceptsMethods('PUT')
@NeedsJSON
def addToPlaylist(request, event_id):
  user = getUserForTicket(request)
  songsToAdd = json.loads(request.raw_post_data)
  for song_request in songsToAdd:
    if not hasBeenAdded(song_request, event_id, user):
      addSong2ActivePlaylist(song_request, event_id, user)
  
  return HttpResponse(status = 201)

@csrf_exempt
@NeedsAuth
@InParty
@AcceptsMethods('POST')
def voteSongDown(request, event_id, playlist_id, user_id):
  return voteSong(event_id, playlist_id, user_id, DownVote)

@csrf_exempt
@NeedsAuth
@InParty
@AcceptsMethods('POST')
def voteSongUp(request, event_id, playlist_id, user_id):
  return voteSong(event_id, playlist_id, user_id, UpVote)

def hasAlreadyVoted(votingUser, entryToVote, VoteType):
  return VoteType.objects.filter(
    user=votingUser, playlist_entry=entryToVote).exists()

def voteSong(event_id, playlist_id, user_id, VoteType):
  votingUser = User.objects.get(pk=user_id)
  entryToVote = get_object_or_404(ActivePlaylistEntry, pk=playlist_id)
  if hasAlreadyVoted(votingUser, entryToVote, VoteType):
    return HttpResponseForbidden()

  VoteType(playlist_entry=entryToVote, user=votingUser).save()
  return HttpResponse()

@NeedsAuth
@IsEventHost
@AcceptsMethods('DELETE')
def removeSongFromActivePlaylist(request, event_id, playlist_id):
  toRemove = get_object_or_404(
    ActivePlaylistEntry, event__id=event_id, id=playlist_id)
  toRemove.state=u'RM'
  toRemove.save()
  return HttpResponse()

@NeedsAuth
@InParty
@TicketUserMatch
@AcceptsMethods('GET')
def getAddRequests(request, event_id, user_id):
  addRequests = ActivePlaylistEntry.objects.filter(
    event__id=event_id, adder__id=user_id).only('client_request_id')
  requestIds = [add_request.client_request_id for add_request in addRequests]
  return HttpResponse(json.dumps(requestIds))

@NeedsAuth
@InParty
@TicketUserMatch
@AcceptsMethods('GET')
def getVotes(request, event_id, user_id):
  upVotes = UpVote.objects.filter(
    playlist_entry__event__id=event_id,
    user__id=user_id, playlist_entry__state=u'QE')
  upvoteIds = [vote.playlist_entry.id for vote in upVotes]
  downVotes = DownVote.objects.filter(
    playlist_entry__event__id=event_id,
    user__id=user_id, playlist_entry__state=u'QE')
  downvoteIds = [vote.playlist_entry.id for vote in downVotes]
  return HttpResponse(json.dumps(
    {'up_vote_ids' : upvoteIds, 'down_vote_ids' : downvoteIds}))
  
