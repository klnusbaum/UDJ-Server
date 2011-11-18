"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.headers import getTicketHeader
from udj.headers import getUserIdHeader
from udj.models import Ticket
from udj.models import LibraryEntry
import json
from datetime import datetime

class AuthTestCase(TestCase):
  fixtures = ['test_fixture.json']

  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test1', 'password' : 'onetest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header(getTicketHeader()))
    self.assertTrue(response.has_header(getUserIdHeader()))
    testUser = User.objects.filter(username='test1')
    self.assertEqual(
      int(response.__getitem__(getUserIdHeader())), testUser[0].id)
    ticket = Ticket.objects.filter(user=testUser)
    self.assertEqual(response.__getitem__(getTicketHeader()), ticket[0].ticket_hash)


class NeedsAuthTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  def setUp(self):
    response = self.client.post(
      '/udj/auth/', {'username': 'test1', 'password' : 'onetest'})
    self.ticket_hash = response.__getitem__(getTicketHeader())
    self.user_id = response.__getitem__(getUserIdHeader())

class DoesServerOpsTestCase(NeedsAuthTestCase):

  def doJSONPut(self, url, payload):
   return self.client.put(
      url,
      data=payload, content_type='text/json', 
      **{getTicketHeader() : self.ticket_hash})

  def doGet(self, url):
    return self.client.get(url, **{getTicketHeader() : self.ticket_hash})
   
  def doDelete(self, url):
    return self.client.delete(url, **{getTicketHeader() : self.ticket_hash})
   
def verifySongAdded(testObject, lib_id, ids, song, artist, album):
  matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, 
    owning_user=testObject.user_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted song.")
  insertedLibEntry = matchedEntries[0]
  testObject.assertEqual(insertedLibEntry.song, song)
  testObject.assertEqual(insertedLibEntry.artist, artist)
  testObject.assertEqual(insertedLibEntry.album, album)

  testObject.assertTrue(lib_id in ids)


class LibSingleAddTestCase(DoesServerOpsTestCase):
  def testLibAdd(self):

    lib_id = 1
    song = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    payload = '[{' + \
     '"id" : ' + str(lib_id) + ',' +\
     '"song" : "' + song + '",'+\
     '"artist" : "' + artist +'",'+\
     '"album" : "' + album + '"}]'


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)
    self.assertEqual(response.status_code, 201)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id, ids, song, artist, album)


class LibMultiAddTestCase(DoesServerOpsTestCase):
  def testLibAdds(self):

    lib_id1 = 1
    song1 = 'Roulette Dares'
    artist1 = 'The Mars Volta'
    album1 = 'Deloused in the Comatorium'

    lib_id2 = 2
    song2 = 'Ilyena'
    artist2 = 'The Mars Volta'
    album2 = 'The Bedlam in Goliath'

    payload = '[{' + \
      '"id" : ' + str(lib_id1) + ',' + \
      '"song" : "' + song1 + '",' + \
      '"artist" : "' + artist1 + '",' + \
      '"album" : "' + album1 + '"},{' + \
      '"id" : ' + str(lib_id2) + ',' + \
      '"song" : "' + song2 + '",' + \
      '"artist" : "' + artist2 + '",' + \
      '"album" : "' + album2 + '"}]'


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)

    self.assertEqual(response.status_code, 201, msg=response.content)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id1, ids, song1, artist1, album1)
    verifySongAdded(self, lib_id2, ids, song2, artist2, album2)

class LibTestDuplicateAdd(DoesServerOpsTestCase):
  def testDupAdd(self):

    payload = []
    payload.append({"song" : "Deep Inside Of You", "artist" : "Third Eye Blind",
      "albumt" : "Blue", "id" : 10})
    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload))

    self.assertEqual(response.status_code, 201, msg=response.content)
    ids = json.loads(response.content)
    self.assertEqual(ids[0], 10)
    self.assertEqual(len(LibraryEntry.objects.filter(owning_user__id=2, host_lib_song_id=10)), 1)
    
class LibRemoveTestCase(DoesServerOpsTestCase):
  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/10')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(LibraryEntry.objects.filter(host_lib_song_id=2,owning_user__id=2)),
      0
    )


class LibFullDeleteTest(DoesServerOpsTestCase):
  def testFullDelete(self):
    response = self.doDelete('/udj/users/'+self.user_id+'/library')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(LibraryEntry.objects.filter(owning_user__id=2)),
      0
    )

class GetEventsTest(DoesServerOpsTestCase):
  def testGetEvents(self):
    response = self.doGet('/udj/events/48.2222/-88.44454')
    self.assertEqual(response.status_code, 200)
    events = json.loads(response.content)
    self.assertEqual(events[0]['id'], 1) 
    self.assertEqual(events[0]['name'], 'First Party') 
    self.assertEqual(events[0]['latitude'], 40.113523) 
    self.assertEqual(events[0]['longitude'], -88.224006) 

