import json
from django.contrib.auth.models import User
from udj.tests.testcases import User1TestCase
from udj.tests.testcases import User2TestCase
from udj.tests.testcases import User3TestCase
from udj.tests.testcases import User4TestCase
from udj.models import Event
from udj.models import LibraryEntry
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import ActivePlaylistEntryId
from udj.models import FinishedEvent
from udj.models import DeletedPlaylistEntry
from udj.models import FinishedPlaylistEntry
from udj.models import AvailableSong
from udj.models import PlayedPlaylistEntry
from udj.models import CurrentSong
from decimal import Decimal
from datetime import datetime

class GetEventsTest(User1TestCase):
  def testGetNearbyEvents(self):
    response = self.doGet('/udj/events/48.2222/-88.44454')
    self.assertEqual(response.status_code, 200)
    events = json.loads(response.content)
    self.assertEqual(events[0]['id'], 1) 
    self.assertEqual(events[0]['name'], 'First Party') 
    self.assertEqual(events[0]['latitude'], 40.113523) 
    self.assertEqual(events[0]['longitude'], -88.224006) 
    self.assertTrue("password" not in events[0])
    self.assertTrue("password_hash" not in events[0])

  def testGetEvents(self):
    response = self.doGet('/udj/events?name=party')
    self.assertEqual(response.status_code, 200)
    events = json.loads(response.content)
    self.assertEqual(len(events), 2)

class CreateEventTest(User2TestCase):
  def testCreateEvent(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    givenEventId = json.loads(response.content)['event_id']
    addedEvent = Event.objects.get(id=givenEventId)
    self.assertEqual(addedEvent.name, partyName)
    partyHost  = EventGoer.objects.get(event__id=givenEventId, user__id=3)



class EndEventTest(User1TestCase):
  def testEndEvent(self):
    response = self.doDelete('/udj/events/1')
    self.assertEqual(len(Event.objects.filter(id=1)), 0)

    finishedEvent = FinishedEvent.objects.get(id=1)
    self.assertEqual(finishedEvent.name, 'First Party') 
    self.assertEqual(finishedEvent.latitude, Decimal('40.113523'))
    self.assertEqual(finishedEvent.longitude, Decimal('-88.224006'))
    self.assertEqual(finishedEvent.host.id, 2)

    finishedSongs = FinishedPlaylistEntry.objects.filter(event=finishedEvent)
    self.assertEqual(len(finishedSongs),2)
    self.assertTrue(FinishedPlaylistEntry.objects.filter(song__id=12).exists())
    self.assertTrue(FinishedPlaylistEntry.objects.filter(song__id=10).exists())
    
    self.assertEqual(
      len(AvailableSong.objects.filter(library_entry__owning_user__id=2)),0)
    self.assertFalse(DeletedPlaylistEntry.objects.filter(event__id=1).exists())


class EndEventTestNoCurrentSong(User4TestCase):
  def testEndEventNoCurrentSong(self):
    response = self.doDelete('/udj/events/2')
    self.assertEqual(len(Event.objects.filter(id=2)), 0)

    finishedEvent = FinishedEvent.objects.get(event_id=2)
    self.assertEqual(finishedEvent.name, 'Second Party') 
    self.assertEqual(finishedEvent.latitude, Decimal('40.113523'))
    self.assertEqual(finishedEvent.longitude, Decimal('-88.224006'))
    self.assertEqual(finishedEvent.host.id,5)
    self.assertEqual(
      len(AvailableSong.objects.filter(library_entry__owning_user__id=5)),0)

    finishedSongs = FinishedPlaylistEntry.objects.filter(event=finishedEvent)
    self.assertEqual(len(finishedSongs),0)


class JoinEventTest(User3TestCase):
  def testJoinEvent(self):
    response = self.doPut('/udj/events/1/user')
    self.assertEqual(response.status_code, 201)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=3)
    self.assertEqual(len(event_goer_entries),1) 
    
class LeaveEventTest(User2TestCase):
  def testLeaveEvent(self):
    response = self.doDelete('/udj/events/1/3')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=3)
    self.assertEqual(len(event_goer_entries), 0)

class KickUserTest(User1TestCase):
  def testKickUser(self):
    response = self.doDelete('/udj/events/1/3')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=3)
    self.assertEqual(len(event_goer_entries), 0)

#TODO still need to test the max_results parameter
class TestGetAvailableMusic(User2TestCase):
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
   
class TestGetCurrentSong(User2TestCase):
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
