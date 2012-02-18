import json
from django.contrib.auth.models import User
from udj.tests.testhelpers import User2TestCase
from udj.tests.testhelpers import User3TestCase
from udj.tests.testhelpers import User4TestCase
from udj.tests.testhelpers import User5TestCase
from udj.tests.testhelpers import User8TestCase
from udj.models import Event
from udj.models import EventEndTime
from udj.models import LibraryEntry
from udj.models import Ticket
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import AvailableSong
from decimal import Decimal
from datetime import datetime
from udj.headers import getGoneResourceHeader, getDjangoUUIDHeader

class GetEventsTest(User5TestCase):
  def testGetNearbyEvents(self):
    #TODO This needs to be more robust, however the location functionality
    # isn't fully working just yet
    response = self.doGet('/udj/events/40.11381/-88.224083')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
    events = json.loads(response.content)
    self.assertEqual(len(events), 2)


  def testGetEvents(self):
    response = self.doGet('/udj/events?name=empty')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
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
    self.verifyJSONResponse(response)
    givenEventId = json.loads(response.content)['event_id']
    addedEvent = Event.objects.get(pk=givenEventId)
    self.assertEqual(addedEvent.name, partyName)
    partyHost = EventGoer.objects.get(event=addedEvent, user__id=self.user_id)



class EndEventTest(User2TestCase):
  def testEndEvent(self):
    response = self.doDelete('/udj/events/2')
    self.assertEqual(Event.objects.get(pk=2).state,u'FN')
    EventEndTime.objects.get(event__id=2)
    EventGoer.objects.get(user__id=2, event__id=2, state=u'LE')

  def testDoubleEnd(self):
    response = self.doDelete('/udj/events/2')
    response = self.doDelete('/udj/events/2')

class EndEmptyEventTest(User4TestCase):
  def testEndEmptyEvent(self):
    response = self.doDelete('/udj/events/3')
    self.assertEqual(Event.objects.get(pk=3).state,u'FN')
    EventGoer.objects.get(user__id=4, event__id=3, state=u'LE')


class JoinEventTest(User5TestCase):
  def testJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')

  def testDoubleJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')

  def testJoinLeaveJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')
    response = self.doDelete('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 200)
    leftevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'LE')
    response = self.doPut('/udj/events/4/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=4, user__id=5, state=u'IE')

  def testJoinEndedEvent(self):
    response = self.doPut('/udj/events/1/users/5')
    self.assertEqual(response.status_code, 410)
    self.assertEqual(response[getGoneResourceHeader()], "event")
    shouldntBeThere = EventGoer.objects.filter(event__id=1, user__id=5)
    self.assertFalse(shouldntBeThere.exists())
    
class LeaveEventTest(User3TestCase):
  def testLeaveEvent(self):
    response = self.doDelete('/udj/events/2/users/3')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.get(
      event__id=2, user__id=3, state=u'LE')

class LeaveEndedEventTest(User8TestCase):
  def testLeaveEndedEvent(self):
    response = self.doDelete('/udj/events/1/users/8')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.get(
      event__id=1, user__id=8, state=u'LE')
  
    


#Disabling this for now. We'll come back to it later.
"""
class KickUserTest(User2TestCase):
  def testKickUser(self):
    userId=4
    response = self.doDelete('/udj/events/1/users/'+str(userId))
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=userId)
    self.assertEqual(len(event_goer_entries), 0)
"""

class TestGetAvailableMusic(User3TestCase):
  def verifyExpectedResults(self, results, realSongs):
    realIds = [song.song.host_lib_song_id for song in realSongs]
    for song in results:
      self.assertTrue(song['id'] in realIds)
 
  def testGetAlbum(self): 
    response = self.doGet('/udj/events/2/available_music?query=blue')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    realSongs = AvailableSong.objects.filter(song__album="Blue")
    self.verifyExpectedResults(results, realSongs)

  def testMaxResults(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=blue&max_results=1')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
 
  def testGetArtist(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=third+eye+blind')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 3)
    realSongs = AvailableSong.objects.filter(song__artist="Third Eye Blind")
    self.verifyExpectedResults(results, realSongs)

  def testGetTitle(self):
    response = self.doGet(
      '/udj/events/2/available_music?query=Never+Let+You+Go')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    realSongs = AvailableSong.objects.filter(song__title="Never Let You Go")
    self.verifyExpectedResults(results, realSongs)

  def testSongNotAvailable(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=water+landing')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 0)

  def testSongsDontExist(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=smashing+pumpkins')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 0)

  def testGetRandoms(self):
    response = self.doGet(
      '/udj/events/2/available_music/random_songs')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)

class TestPutAvailableMusic(User2TestCase):
  def testSimplePut(self): 
    toAdd=[6]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0], 6)
    AvailableSong.objects.get(
      song__host_lib_song_id=6, song__owning_user__id=2)

  def testMultiPut(self):
    toAdd = [6,7]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(6 in results)
    self.assertTrue(7 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=6, song__owning_user__id=2)
    AvailableSong.objects.get(
      song__host_lib_song_id=7, song__owning_user__id=2)

  def testDoublePut(self):
    toAdd = [8]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertTrue(8 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=8, song__owning_user__id=2)

    toAdd = [7, 8]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(7 in results)
    self.assertTrue(8 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=7, song__owning_user__id=2)
    AvailableSong.objects.get(
      song__host_lib_song_id=8, song__owning_user__id=2)

class TestCantPutAvailableMusic(User3TestCase):
  def testPut(self):
   toAdd=[7]
   response = self.doJSONPut('/udj/events/2/available_music', json.dumps(toAdd))
   self.assertEqual(response.status_code, 403, response.content)

class TestDeleteAvailableMusic(User2TestCase):
  def testRemove(self):
    response = self.doDelete('/udj/events/2/available_music/3')
    self.assertEqual(response.status_code, 200, response.content)
    foundSongs = AvailableSong.objects.filter(
      song__host_lib_song_id=3, song__owning_user__id=2)
    self.assertFalse(foundSongs.exists())

  def testBadRemove(self):
    response = self.doDelete('/udj/events/2/available_music/400')
    self.assertEqual(response.status_code, 404, response.content)

  def testRemoveSongAlsoUsedInPreviousEvent(self):
    response = self.doDelete('/udj/events/2/available_music/1')
    self.assertEqual(response.status_code, 200, response.content)



class TestSetCurrentSong(User2TestCase):
  def testSetCurrentSong(self):
    response = self.doPost(
      '/udj/events/2/current_song', 
      {'playlist_entry_id' : '4'})
    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=4).state, u'PL')
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=5).state, u'FN')

  def testSetWithNoCurrentSong(self):
    currentSong = ActivePlaylistEntry.objects.get(pk=5)
    currentSong.state = u'FN'
    currentSong.save()
    response = self.doPost(
      '/udj/events/2/current_song',
      {'playlist_entry_id' : '4'})
    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=4).state, u'PL')

class TestDuplicateHostEventCreate(User2TestCase):
  def testDuplicatHostEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName }
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 409)

class TestDoubleEventCreate(User5TestCase):
  def testDoubleEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    self.verifyJSONResponse(response)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))
    self.assertEqual(response.status_code, 200)
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    self.verifyJSONResponse(response)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))

class TestGetEventGoers(User3TestCase):
  def testRegularGetEventGoers(self):
    event_id = 2
    response = self.doGet('/udj/events/' + str(event_id) + '/users')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
    eventGoersJson = json.loads(response.content)
    eventGoers = EventGoer.objects.filter(event__id=event_id)
    self.assertEqual(len(eventGoersJson), len(eventGoers))
    jsonIds = [eg['id'] for eg in eventGoersJson]
    for eg in eventGoers:
      self.assertTrue(eg.user.id in jsonIds)
