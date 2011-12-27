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
from udj.models import ActivePlaylistEntryId
from udj.models import LibraryEntry
from udj.models import Event
from udj.models import CurrentSong
from udj.models import UpVote
from udj.models import DownVote
from udj.models import PlayedPlaylistEntry
from udj.models import DeletedPlaylistEntry
from udj.JSONCodecs import getJSONForActivePlaylistEntries
from udj.JSONCodecs import getActivePlaylistEntryDictionary
from udj.JSONCodecs import getJSONForPreviousAddRequests
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
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.entry_id_id',

        'downvotes' : 'select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.entry_id_id',
        'total_votes' : '(SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.entry_id_id)-' +\
        '(select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.entry_id_id)'
      },
      order_by = ['-total_votes', 'time_added'])
    
  return HttpResponse(getJSONForActivePlaylistEntries(playlistEntries))

def hasBeenAdded(song_request, event_id, user):
  return \
    ActivePlaylistEntry.objects.filter(
      adder=user, 
      client_request_id=song_request['client_request_id'],
      event__event_id__id=event_id
    ).exists() \
  or \
    CurrentSong.objects.filter(
      event__event_id__id=event_id, 
      adder=user, 
      client_request_id=song_request['client_request_id']
    ).exists() \
  or \
    PlayedPlaylistEntry.objects.filter(
      event__event_id__id=event_id,
      adder=user, 
      client_request_id=song_request['client_request_id']
    ).exists() \
  or \
    DeletedPlaylistEntry.objects.filter(
      event__event_id__id=event_id,
      adder=user, 
      client_request_id=song_request['client_request_id']
    ).exists()

  
def addSong2ActivePlaylist(song_request, event_id, adding_user):
  event = Event.objects.get(event_id__id=event_id)
  songToAdd = LibraryEntry.objects.get(
      host_lib_song_id=song_request['lib_id'], owning_user=event.host)
  new_entry_id = ActivePlaylistEntryId()
  new_entry_id.save()
  added = ActivePlaylistEntry(
    entry_id=new_entry_id,
    song=songToAdd,
    adder=adding_user,
    event=event,
    client_request_id=song_request['client_request_id'])
  added.save()
  UpVote(playlist_entry=new_entry_id, user=adding_user).save()

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
def voteSongDown(request, event_id, playlist_id):
  return voteSong(request, event_id, playlist_id, DownVote)

@csrf_exempt
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
  entryToVote = get_object_or_404(ActivePlaylistEntryId, pk=playlist_id)
  if hasAlreadyVoted(votingUser, entryToVote, VoteType):
    return HttpResponseForbidden()

  VoteType(playlist_entry=entryToVote, user=votingUser).save()
  return HttpResponse()

@NeedsAuth
@IsEventHost
@AcceptsMethods('DELETE')
def removeSongFromActivePlaylist(request, event_id, playlist_id):
  if DeletedPlaylistEntry.objects.filter(entry_id__id=playlist_id).exists():
    return HttpResponse()

  toRemove = get_object_or_404(
    ActivePlaylistEntry, entry_id__id=playlist_id, event__id=event_id)
  current_entry_id = get_object_or_404(ActivePlaylistEntryId, pk=playlist_id)
  DeletedPlaylistEntry(entry_id=current_entry_id, adder=toRemove.adder,
    song=toRemove.song, event=toRemove.event, 
    client_request_id=toRemove.client_request_id).save()
  toRemove.delete()
  return HttpResponse()

@NeedsAuth
@InParty
@TicketUserMatch
@AcceptsMethods('GET')
def getAddRequests(request, event_id, user_id):
  inQueue = ActivePlaylistEntry.objects.filter(
    event__event_id__id=event_id, adder__id=user_id);
  deletedEntries = DeletedPlaylistEntry.objects.filter(
    event__event_id__id=event_id, adder__id=user_id)
  playedEntries = PlayedPlaylistEntry.objects.filter(
    event__event_id__id=event_id, adder__id=user_id)
  currentSong = None
  try:
    currentSong = CurrentSong.objects.get(event__event_id__id=event_id)
  except ObjectDoesNotExist:
    pass 
  return HttpResponse(getJSONForPreviousAddRequests(inQueue, deletedEntries,
    playedEntries, currentSong, user_id)) 

@NeedsAuth
@InParty
@TicketUserMatch
@AcceptsMethods('GET')
def getVotes(request, event_id, user_id):
  activePlaylist = ActivePlaylistEntry.objects.filter(
    event__event_id__id=event_id).only("entry_id")
  activeIds = [entry.entry_id.id for entry in activePlaylist]
  downVotes = DownVote.objects.filter(
    user__id=user_id, playlist_entry__in=activeIds).only('playlist_entry')
  downvoteIds = [vote.playlist_entry.id for vote in downVotes]
  upVotes = UpVote.objects.filter(
    user__id=user_id, playlist_entry__in=activeIds).only('playlist_entry')
  upvoteIds = [vote.playlist_entry.id for vote in upVotes]
  return HttpResponse(json.dumps(
    {'up_vote_ids' : upvoteIds, 'down_vote_ids' : downvoteIds}))
  
