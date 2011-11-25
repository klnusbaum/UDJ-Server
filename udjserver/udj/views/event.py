import json
import hashlib
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from udj.auth import getUserForTicket
from udj.decorators import TicketUserMatch
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import IsEventHost
from udj.decorators import CanLoginToEvent
from udj.decorators import IsUserOrHost
from udj.decorators import InParty
from udj.models import Event
from udj.models import LibraryEntry
from udj.models import AvailableSong
from udj.models import EventGoer
from udj.models import CurrentSong
from udj.models import FinishedEvent
from udj.models import FinishedPlaylistEntry
from udj.models import PlayedPlaylistEntry
from udj.models import ActivePlaylistEntry
from udj.models import UpVote
from udj.models import DownVote
from udj.JSONCodecs import getJSONForEvents
from udj.JSONCodecs import getJSONForAvailableSongs
from udj.JSONCodecs import getJSONForCurrentSong


@AcceptsMethods('GET')
@NeedsAuth
def getNearbyEvents(request, latitude, longitude):
  #TODO actually have this only return nearby events
  events = Event.objects.all()
  events_json = getJSONForEvents(events)
  return HttpResponse(events_json)  

@AcceptsMethods('PUT')
@NeedsJSON
@NeedsAuth
def createEvent(request):
  user = getUserForTicket(request)
  event = json.loads(request.raw_post_data)

  if 'name' not in event:
    return HttpResponseBadRequest("Must include a name attribute")
  toInsert = Event(name=event['name'], host=user)

  if 'coords' in event:
    if 'latitude' not in event['coords'] or 'longitude' not in event['coords']:
      return HttpResponseBadRequest("Must include both latitude and "
        "longitude with coords")
    else:
      toInsert.latitude = event['coords']['latitude']
      toInsert.longitude = event['coords']['longitude']

  if 'password' in event:
    m = hashlib.sha1()
    m.update(event[password])
    toInsert.password_hash = m.hexdigest()
      
  toInsert.save()
  return HttpResponse('{"event_id" : ' + str(toInsert.id) + '}', status=201)
       
def savePlayedSongs(endingEvent, finishedEvent):
  for playedSong in PlayedPlaylistEntry.objects.filter(event=endingEvent):
    FinishedPlaylistEntry(
      song = playedSong.song,
      upvotes = playedSong.upvotes,
      downvotes = playedSong.downvotes,
      time_added = playedSong.time_added,
      time_played = playedSong.time_played,
      adder = playedSong.adder,
      event = finishedEvent).save()

def saveCurrentSong(endEvent, finishedEvent):
  currentSong = CurrentSong.objects.get(event=endEvent)
  FinishedPlaylistEntry(
    song = currentSong.song,
    upvotes = currentSong.upvotes,
    downvotes = currentSong.downvotes,
    time_added = currentSong.time_added,
    time_played = currentSong.time_played,
    adder = currentSong.adder,
    event = finishedEvent).save()
      

#Should be able to make only one call to the events table to ensure it:
# 1. Exsits
# 2. This user is the host
# 3. Moved it to finished events and delete it.
# Right now these are all done seperately. 
#This is a potental future optimization
@AcceptsMethods('DELETE')
@NeedsAuth
@IsEventHost
def endEvent(request, event_id):
  #TODO We have a race condition here. Gonna need to wrap this in a transaction
  #in the future
  toDelete = Event.objects.get(id=event_id)
  host = toDelete.host
  finishedEvent = FinishedEvent(
    event_id=toDelete.id,
    name=toDelete.name, 
    host=toDelete.host, 
    latitude = toDelete.latitude,
    longitude = toDelete.longitude,
    time_started = toDelete.time_started)
  finishedEvent.save() 

  savePlayedSongs(toDelete, finishedEvent)
  saveCurrentSong(toDelete, finishedEvent)
  toDelete.delete()
  AvailableSong.objects.filter(library_entry__owning_user=host).delete()
  
  return HttpResponse("Party ended")


@AcceptsMethods('PUT')
@NeedsAuth
@CanLoginToEvent
def joinEvent(request, event_id):
  joining_user = getUserForTicket(request)
  event_to_join = Event.objects.get(id=event_id)
  event_goer = EventGoer(user=joining_user, event=event_to_join)
  event_goer.save()
  return HttpResponse("joined event", status=201)

@AcceptsMethods('DELETE')
@NeedsAuth
@IsUserOrHost
def leaveEvent(request, event_id, user_id):
  event_goer = EventGoer.objects.get(event__id=event_id, user__id=user_id)
  event_goer.delete()
  return HttpResponse("left event")

@NeedsAuth
@AcceptsMethods(['GET', 'PUT'])
def availableMusic(request, event_id):
  if request.method == 'GET':
    return getAvailableMusic(request, event_id=event_id)
  else:
    return addToAvailableMusic(request, event_id=event_id)

@InParty
def getAvailableMusic(request, event_id):
  event = Event.objects.get(pk=event_id)
  if(not request.GET.__contains__('query')):
    return HttpResponseBadRequest('Must specify query')
  query = request.GET.__getitem__('query')
  available_songs = AvailableSong.objects.filter(
    Q(library_entry__owning_user=event.host),
    Q(library_entry__song__icontains=query) | 
    Q(library_entry__artist__icontains=query) |
    Q(library_entry__album__icontains=query))
  if(request.GET.__contains__('max_results')):
    available_songs = available_songs[:request.GET['max_results']]
    
  return HttpResponse(getJSONForAvailableSongs(available_songs))

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getRandomMusic(request, event_id):
  rand_limit = request.GET.get('max_randoms',20)
  randomSongs = AvailableSong.objects.order_by('?')[:rand_limit]
  return HttpResponse(getJSONForAvailableSongs(randomSongs))

@IsEventHost
@NeedsJSON
def addToAvailableMusic(request, event_id):
  host = getUserForTicket(request)
  toAdd = json.loads(request.raw_post_data)
  added = []
  for song_id in toAdd:
    addSong = AvailableSong(library_entry=LibraryEntry.objects.get(
      host_lib_song_id=song_id, owning_user=host))
    addSong.save()
    added.append(song_id)

  return HttpResponse(json.dumps(added), status=201)

@NeedsAuth
@AcceptsMethods('DELETE')
@IsEventHost
def removeFromAvailableMusic(request, event_id, song_id):
  host = getUserForTicket(request)
  try:
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=song_id,
      library_entry__owning_user=host).delete()
  except DoesNotExist:
    return HttpResponseNotFound("id " + str(song_id) + " doesn't exist")
  return HttpResponse()

@NeedsAuth
@AcceptsMethods(['GET', 'POST'])
def currentSong(request, event_id):
  if request.method == 'GET':
    return getCurrentSong(request, event_id=event_id)
  else: 
    return setCurrentSong(request, event_id=event_id)

@InParty
def getCurrentSong(request, event_id):
  currentSong = CurrentSong.objects.get(event__id=event_id)
  return HttpResponse(getJSONForCurrentSong(currentSong))

def moveCurrentSong2PlayedSong(given_event):
  currentSong = CurrentSong.objects.get(event=given_event)
  PlayedPlaylistEntry(
    song = currentSong.song,
    upvotes = currentSong.upvotes,
    downvotes = currentSong.downvotes,
    time_added = currentSong.time_added,
    time_played = currentSong.time_played,
    adder = currentSong.adder,
    event = given_event,
    client_request_id = currentSong.client_request_id).save()
  currentSong.delete()
  
def movePlaylistEntry2CurrentSong(given_event, playlist_entry_id):
  playlistEntry = get_object_or_404(ActivePlaylistEntry, pk=playlist_entry_id)
  CurrentSong( 
    song = playlistEntry.song,
    upvotes = UpVote.objects.filter(playlist_entry=playlistEntry).count(),
    downvotes = DownVote.objects.filter(playlist_entry=playlistEntry).count(),
    time_added = playlistEntry.time_added,
    adder = playlistEntry.adder,
    event = given_event,
    client_request_id = playlistEntry.client_request_id).save()
  playlistEntry.delete()

@IsEventHost
def setCurrentSong(request, event_id):
  if(not request.POST.__contains__('playlist_entry_id')):
    return HttpResponseBadRequest(
      'Please specifiy the playlist entry to set as the current song')
  event = Event.objects.get(pk=event_id) 
  moveCurrentSong2PlayedSong(event)
  movePlaylistEntry2CurrentSong(
    event, request.POST.__getitem__('playlist_entry_id'))
  return HttpResponse("Song changed")
  
