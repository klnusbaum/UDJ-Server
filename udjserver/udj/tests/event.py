import json
from django.contrib.auth.models import User
from udj.tests.testcases import User2TestCase
from udj.tests.testcases import User3TestCase
from udj.tests.testcases import User4TestCase
from udj.tests.testcases import User5TestCase
from udj.models import Event
from udj.models import LibraryEntry
from udj.models import Ticket
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import AvailableSong
from decimal import Decimal
from datetime import datetime

class GetEventsTest(User5TestCase):
  def testGetNearbyEvents(self):
    #TODO This needs to be more robust, however the location functionality
    # isn't fully working just yet
    response = self.doGet('/udj/events/48.2222/-88.44454')
    self.assertEqual(response.status_code, 200)
    events = json.loads(response.content)
    self.assertEqual(len(events), 2)


  def testGetEvents(self):
    response = self.doGet('/udj/events?name=empty')
    self.assertEqual(response.status_code, 200)
    events = json.loads(response.content)
    self.assertEqual(len(events), 1)
    emptyEvent = events[0]
    self.assertEqual(int(emptyEvent['id']), 3)
    self.assertEqual(emptyEvent['longitude'], -88.224006)
    self.assertEqual(emptyEvent['latitude'], 40.113523)
    self.assertEqual(int(emptyEvent['host_id']), 4)
    self.assertEqual(emptyEvent['host_username'], 'test4')
    self.assertEqual(emptyEvent['has_password'], False)

class CreateEventTest(User5TestCase):
  def testCreateEvent(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    givenEventId = json.loads(response.content)['event_id']
    addedEvent = Event.objects.get(pk=givenEventId)
    self.assertEqual(addedEvent.name, partyName)
    partyHost = EventGoer.objects.get(event=addedEvent, user__id=self.user_id)



class EndEventTest(User2TestCase):
  def testEndEvent(self):
    response = self.doDelete('/udj/events/2')
    self.assertEqual(Event.objects.get(pk=2).state,u'FN')

class EndEmptyEventTest(User4TestCase):
  def testEndEmptyEvent(self):
    response = self.doDelete('/udj/events/3')
    self.assertEqual(Event.objects.get(pk=3).state,u'FN')


class JoinEventTest(User5TestCase):
  def testJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=2, user__id=5)
    self.assertEqual(len(event_goer_entries),1) 

  def testDoubleJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    event_goer_entries = EventGoer.objects.get(event__id=2, user__id=5)
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    event_goer_entries = EventGoer.objects.get(event__id=2, user__id=5)
    
"""
class LeaveEventTest(User3TestCase):
  def testLeaveEvent(self):
    response = self.doDelete('/udj/events/1/users/4')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=4)
    self.assertEqual(len(event_goer_entries), 0)

"""

#Disabling this for now. We'll come back to it later.
"""
class KickUserTest(User1TestCase):
  def testKickUser(self):
    userId=4
    response = self.doDelete('/udj/events/1/users/'+str(userId))
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=userId)
    self.assertEqual(len(event_goer_entries), 0)
"""

#TODO still need to test the max_results parameter
"""
class TestGetAvailableMusic(User3TestCase):
  def verifyExpectedResults(self, results, realSongs):
   realIds = [song.host_lib_song_id for song in realSongs]
   for song in results:
     self.assertTrue(song['id'] in realIds)
 
  def testGetAlbum(self): 
   response = self.doGet('/udj/events/1/available_music?query=blue')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)
   self.assertEqual(len(results), 2)
   realSongs = LibraryEntry.objects.filter(album="Blue")
   self.verifyExpectedResults(results, realSongs)

  def testMaxResults(self): 
   response = self.doGet(
    '/udj/events/1/available_music?query=blue&max_results=1')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)
   self.assertEqual(len(results), 1)

  def testGetArtist(self): 
   response = self.doGet(
    '/udj/events/1/available_music?query=smashing+pumpkins')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)
   self.assertEqual(len(results), 2)
   realSongs = LibraryEntry.objects.filter(artist="The Smashing Pumpkins")
   self.verifyExpectedResults(results, realSongs)

  def testGetSong(self):
   response = self.doGet(
    '/udj/events/1/available_music?query=Never+Let+You+Go')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)
   self.assertEqual(len(results), 1)
   realSongs = LibraryEntry.objects.filter(song="Never Let You Go")
   self.verifyExpectedResults(results, realSongs)

  def testSongNotAvailable(self): 
   response = self.doGet(
    '/udj/events/1/available_music?query=rage+against+the+machine')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)
   self.assertEqual(len(results), 0)

  def testGetRandoms(self):
   response = self.doGet(
    '/udj/events/1/available_music/random_songs')
   self.assertEqual(response.status_code, 200, response.content)
   results = json.loads(response.content)

class TestPutAvailableMusic(User1TestCase):
  def testSimplePut(self): 
    toAdd=[13]
    response = self.doJSONPut(
      '/udj/events/1/available_music', json.dumps(toAdd))
    self.assertEqual(response.status_code, 201, response.content)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0], 13)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=13, library_entry__owning_user__id=2)

  def testMultiPut(self):
    toAdd = [13,12]
    response = self.doJSONPut(
      '/udj/events/1/available_music', json.dumps(toAdd))
    self.assertEqual(response.status_code, 201, response.content)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(13 in results)
    self.assertTrue(12 in results)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=13, library_entry__owning_user__id=2)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=12, library_entry__owning_user__id=2)

  def testDoublePut(self):
    toAdd = [13]
    response = self.doJSONPut(
      '/udj/events/1/available_music', json.dumps(toAdd))
    self.assertEqual(response.status_code, 201, response.content)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertTrue(13 in results)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=13, library_entry__owning_user__id=2)
    toAdd = [13, 12]
    response = self.doJSONPut(
      '/udj/events/1/available_music', json.dumps(toAdd))
    self.assertEqual(response.status_code, 201, response.content)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(13 in results)
    self.assertTrue(12 in results)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=13, library_entry__owning_user__id=2)
    AvailableSong.objects.get(
      library_entry__host_lib_song_id=12, library_entry__owning_user__id=2)

class TestCantPutAvailableMusic(User2TestCase):
  def testPut(self): 
   toAdd=[13]
   response = self.doJSONPut('/udj/events/1/available_music', json.dumps(toAdd))
   self.assertEqual(response.status_code, 403, response.content)

class TestDeleteAvailableMusic(User1TestCase):
  def testRemove(self):
    response = self.doDelete('/udj/events/1/available_music/10')
    self.assertEqual(response.status_code, 200, response.content)
    foundSongs = AvailableSong.objects.filter(
      library_entry__host_lib_song_id=10, library_entry__owning_user__id=2)
    self.assertEqual(len(foundSongs), 0)
   
class TestGetCurrentSong(User3TestCase):
  def testGetCurrentSong(self):
    response = self.doGet('/udj/events/1/current_song')
    self.assertEqual(response.status_code, 200, response.content)
    result = json.loads(response.content) 
    actualCurrentSong = CurrentSong.objects.get(event__id=1)
    self.assertEqual(
      actualCurrentSong.song.host_lib_song_id, result['lib_song_id'])
    self.assertEqual(actualCurrentSong.song.song, result['song'])
    self.assertEqual(actualCurrentSong.song.artist, result['artist'])
    self.assertEqual(actualCurrentSong.song.album, result['album'])
    self.assertEqual(actualCurrentSong.song.duration, result['duration'])
    self.assertEqual(actualCurrentSong.upvotes, result['up_votes'])
    self.assertEqual(actualCurrentSong.downvotes, result['down_votes'])
    self.assertEqual(
      actualCurrentSong.time_added, 
      datetime.strptime(result['time_added'], "%Y-%m-%dT%H:%M:%S"))
    self.assertEqual(
      actualCurrentSong.time_played, 
      datetime.strptime(result['time_played'], "%Y-%m-%dT%H:%M:%S"))
    self.assertEqual(actualCurrentSong.adder.id, result['adder_id'])

class TestSetCurentSong(User1TestCase):
  def testSetCurrentSong(self):
    response = self.doPost(
      '/udj/events/1/current_song', 
      {'playlist_entry_id' : '5'})
    self.assertEqual(response.status_code, 200, response.content)
    movedActivePlaylistEntry = ActivePlaylistEntry.objects.filter(pk=5)  
    self.assertFalse(movedActivePlaylistEntry.exists())
    newCurrent = CurrentSong.objects.get(client_request_id=2, adder=3, event=1)
    self.assertEqual(newCurrent.upvotes, 3)
    self.assertEqual(newCurrent.downvotes, 0)
    oldCurrent = PlayedPlaylistEntry.objects.get(
      client_request_id=1, adder=3, event=1)

class TestSetCurrentSong2(User4TestCase):
  def testSetWithNoCurrentSong(self):
    libentry = LibraryEntry.objects.get(pk=14)
    AvailableSong(library_entry=libentry).save();
    new_entry_id = ActivePlaylistEntryId()
    new_entry_id.save()
    activeEntry = ActivePlaylistEntry(
      entry_id=new_entry_id,
      song=libentry, adder=User.objects.get(pk=5),
      event=Event.objects.get(pk=2), client_request_id=3)
    activeEntry.save()
    response = self.doPost(
      '/udj/events/2/current_song', 
      {'playlist_entry_id' : str(activeEntry.entry_id.id)})
    self.assertEqual(response.status_code, 200)

class TestDuplicateHostEventCreate(User1TestCase):
  def testDuplicatHostEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 409)

class TestDoubleEventCreate(User2TestCase):
  def testDoubleEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))
    self.assertEqual(response.status_code, 200)
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))

class TestGetEventGoers(User1TestCase):
  def testRegularGetEventGoers(self):
    event_id = 1
    response = self.doGet('/udj/events/' + str(event_id) + '/users')
    self.assertEqual(response.status_code, 200)
    eventGoersJson = json.loads(response.content)
    eventGoers = EventGoer.objects.filter(event__event_id__id=event_id)
    self.assertEqual(len(eventGoersJson), len(eventGoers))
    jsonIds = [eg['id'] for eg in eventGoersJson]
    for eg in eventGoers:
      self.assertTrue(eg.user.id in jsonIds)
"""
