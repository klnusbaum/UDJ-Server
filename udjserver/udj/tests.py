"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
from udj.models import LibraryEntry
import json

def authTestUser(testObject):
    response = testObject.client.post('/udj/auth/', {'username': 'test', 'password' : 'onetest'})
    testObject.ticket_hash = response.__getitem__('udj_ticket_hash')
    testObject.user_id = response.__getitem__('user_id')




class AuthTestCase(TestCase):
  fixtures = ['test_fixture.json']


  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test', 'password' : 'onetest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header('udj_ticket_hash'))
    self.assertTrue(response.has_header('user_id'))
    testUser = User.objects.filter(username='test')
    self.assertEqual(int(response.__getitem__('user_id')), testUser[0].id)
    ticket = Ticket.objects.filter(user=testUser)
    self.assertEqual(response.__getitem__('udj_ticket_hash'), ticket[0].ticket_hash)


class NeedsAuthTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  def setUp(self):
    authTestUser(self)

  def doJSONPut(self, url, payload):
    return self.client.put(
      url,
      data=payload, content_type='text/json', 
      **{'udj_ticket_hash' : self.ticket_hash})
   
  def doDelete(self, url):
    return self.client.delete(url, **{'udj_ticket_hash' : self.ticket_hash})
   

class LibAddTestCase(NeedsAuthTestCase):
  def testLibAdd(self):

    lib_id = 1
    song = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    payload = '[{"server_lib_song_id" : -1, "host_lib_song_id" : ' +\
      str(lib_id) + \
      ', "song" : "' + song + '", "artist" : "' + artist + '" , "album" : "' + \
      album +'"}]'
    response = self.doJSONPut('/udj/users/' + self.user_id + '/library/songs', payload)

    self.assertEqual(response.status_code, 201)
    matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, \
      owning_user=self.user_id)
    self.assertEqual(len(matchedEntries), 1, msg="Couldn't find inserted song.")
    insertedLibEntry = matchedEntries[0]
    self.assertEqual(insertedLibEntry.song, song)
    self.assertEqual(insertedLibEntry.artist, artist)
    self.assertEqual(insertedLibEntry.album, album)

    responseObject = json.loads(response.content)[0]
    self.assertEqual(
      responseObject['server_lib_song_id'], insertedLibEntry.server_lib_song_id)
    self.assertEqual(responseObject['host_lib_song_id'], 1)
    self.assertEqual(responseObject['song'], song)
    self.assertEqual(responseObject['artist'], artist)
    self.assertEqual(responseObject['album'], album)


class LibRemoveTestCase(NeedsAuthTestCase):
  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/2')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(LibraryEntry.objects.filter(server_lib_song_id=2)),
      0
    )


class LibFullDeleteTest(NeedsAuthTestCase):
  def testFullDelete(self):
    response = self.doDelete('/udj/users/'+self.user_id+'/library')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(LibraryEntry.objects.filter(owning_user__id=2)),
      0
    )
