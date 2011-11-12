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


class LibAddTestCase(TestCase):
  fixtures = ['test_fixture.json']


  def testLibAdd(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test', 'password' : 'onetest'})
    ticket_hash = response.__getitem__('udj_ticket_hash')
    user_id = response.__getitem__('user_id')


    lib_id = 1
    song = 'Roulet Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    payload = '{"server_lib_song_id" : -1, "host_lib_song_id" : ' +\
      str(lib_id) + \
      ', "song" : "' + song + '", "artist" : "' + artist + '" , "album" : "' + \
      album +'"}'
    response = client.put('/udj/users/' + user_id + '/library/song', \
      data=payload, content_type='text/json', \
      **{'udj_ticket_hash' : ticket_hash})


    self.assertEqual(response.status_code, 200)
    matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, \
      owning_user=user_id)
    self.assertEqual(len(matchedEntries), 1, msg="Couldn't find inserted song.")
    insertedLibEntry = matchedEntries[0]
    self.assertEqual(insertedLibEntry.song, song)
    self.assertEqual(insertedLibEntry.artist, artist)
    self.assertEqual(insertedLibEntry.album, album)
    
