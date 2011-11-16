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
from udj.models import Playlist
from udj.models import PlaylistEntry
import json
from datetime import datetime

class AuthTestCase(TestCase):
  fixtures = ['test_fixture.json']

  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test1', 'password' : 'onetest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header('udj_ticket_hash'))
    self.assertTrue(response.has_header('user_id'))
    testUser = User.objects.filter(username='test1')
    self.assertEqual(int(response.__getitem__('user_id')), testUser[0].id)
    ticket = Ticket.objects.filter(user=testUser)
    self.assertEqual(response.__getitem__('udj_ticket_hash'), ticket[0].ticket_hash)


class NeedsAuthTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  def setUp(self):
    response = self.client.post(
      '/udj/auth/', {'username': 'test1', 'password' : 'onetest'})
    self.ticket_hash = response.__getitem__('udj_ticket_hash')
    self.user_id = response.__getitem__('user_id')

class DoesServerOpsTestCase(NeedsAuthTestCase):

  def doJSONPut(self, url, payload):
    return self.client.put(
      url,
      data=payload, content_type='text/json', 
      **{'udj_ticket_hash' : self.ticket_hash})
   
  def doDelete(self, url):
    return self.client.delete(url, **{'udj_ticket_hash' : self.ticket_hash})
   
def verifySongAdded(testObject, lib_id, idMap, song, artist, album):
  matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, 
    owning_user=testObject.user_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted song.")
  insertedLibEntry = matchedEntries[0]
  testObject.assertEqual(insertedLibEntry.song, song)
  testObject.assertEqual(insertedLibEntry.artist, artist)
  testObject.assertEqual(insertedLibEntry.album, album)

  testObject.assertEqual( 
    idMap['server_id'], insertedLibEntry.server_lib_song_id)
  testObject.assertEqual(idMap['client_id'], lib_id)


class LibSingleAddTestCase(DoesServerOpsTestCase):
  def testLibAdd(self):

    lib_id = 1
    song = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    payload = '{ "to_add" : [{'\
      ' "song" : "' + song + '", "artist" : "' + artist + '" , "album" : "' + \
      album +'"}], "id_maps" : [ {"server_id" : -1, "client_id" : ' + \
     str(lib_id) +  '}]}'

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)
    self.assertEqual(response.status_code, 201)
    idMap = json.loads(response.content)[0]
    verifySongAdded(self, lib_id, idMap, song, artist, album)



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

    payload = '{ "to_add" : ' + \
      ' [{"song" : "' + song1 + '", "artist" : "' + artist1 + \
      '" , "album" : "' + album1 +'"}, ' + \
      '{"song" : "' + song2 + '", "artist" : "' + artist2 + \
      '" , "album" : "' + album2 +'"}],' + \
      '"id_maps" : [ {"server_id" : -1, "client_id" : ' + \
       str(lib_id1) +'}, ' +  \
      '{"server_id" : -1, "client_id" : ' + str(lib_id2) + '}]}'

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)

    self.assertEqual(response.status_code, 201, msg=response.content)
    response_payload = json.loads(response.content)
    idMap = response_payload[0]
    verifySongAdded(self, lib_id1, idMap, song1, artist1, album1)
    idMap = response_payload[1]
    verifySongAdded(self, lib_id2, idMap, song2, artist2, album2)

class LibRemoveTestCase(DoesServerOpsTestCase):
  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/2')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(LibraryEntry.objects.filter(server_lib_song_id=2)),
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

def verifyPlaylistAdded(testObject, host_id, idMap, name, date_created):
  matchedEntries = Playlist.objects.filter(host_playlist_id=host_id, 
    owning_user=testObject.user_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted playlist.")
  insertedPlaylist = matchedEntries[0]
  testObject.assertEqual(insertedPlaylist.name, name)
  testObject.assertEqual(
    insertedPlaylist.date_created, 
    datetime.fromtimestamp(date_created))

  testObject.assertEqual( 
    idMap['server_id'], insertedPlaylist.server_playlist_id)
  testObject.assertEqual(idMap['client_id'], host_id)


class PlaylistSingleAddTest(DoesServerOpsTestCase):
  def testAddPlaylist(self):
    host_id = 1
    name = "Daft Punk"
    date_created = 1321019418
    payload = '{"to_add" : [{"name" : "' + name + '", "date_created" : ' + \
      str(date_created ) + '}], "id_maps" : [{"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id) + '}]}'

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/playlists', payload)

    self.assertEqual(response.status_code, 201, msg=response.content)
    response_payload = json.loads(response.content)
    idMap = response_payload[0]
    verifyPlaylistAdded(self, host_id, idMap, name, date_created)

class PlaylistMutliAddTest(DoesServerOpsTestCase):
  def testAddPlaylists(self):
    host_id1 = 1
    name1 = "Daft Punk Hits"
    date_created1 = 1321019418
    host_id2 = 2
    name2 = "Milkman Hits"
    date_created2 = 1321020000
    payload = '{"to_add" : [{"name" : "' + name1 + '", "date_created" : ' + \
      str(date_created1) + '}, {"name" : "' + name2 + '", "date_created" : ' + \
      str(date_created2) + '} ], "id_maps" : [{"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id1) + '}, {"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id2) + '}]}'

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/playlists', payload)

    self.assertEqual(response.status_code, 201, msg=response.content)
    response_payload = json.loads(response.content)
    idMap = response_payload[0]
    verifyPlaylistAdded(self, host_id1, idMap, name1, date_created1)
    idMap = response_payload[1]
    verifyPlaylistAdded(self, host_id2, idMap, name2, date_created2)

class PlaylistRemoveTestCase(DoesServerOpsTestCase):
  def testPlaylistDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/playlists/1')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(Playlist.objects.filter(server_playlist_id=1)),0)

def verifyPlaylistEntryAdded(
  testObject, host_id, idMap, lib_song_id, playlist_id):

  matchedEntries = PlaylistEntry.objects.filter(host_playlist_entry_id=host_id, 
    playlist__server_playlist_id=playlist_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted playlist.")
  insertedPlaylistEntry = matchedEntries[0]
  testObject.assertEqual(
    insertedPlaylistEntry.song.server_lib_song_id, lib_song_id)

  testObject.assertEqual( 
    idMap['server_id'], insertedPlaylistEntry.server_playlist_entry_id)
  testObject.assertEqual(idMap['client_id'], host_id)

  

class PlaylistEntrySingleAddTest(DoesServerOpsTestCase):
  def testAddPlaylistEntry(self):
    host_id = 1
    lib_song_id = 6
    playlist_id = 1
    payload = '{"to_add" : ['+ str(lib_song_id) + '],' +\
      '"id_maps" : [{"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id) + '}]}'

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/playlists/'+str(playlist_id)+'/songs',
      payload)
    self.assertEqual(response.status_code, 201, msg=response.content)
    response_payload = json.loads(response.content)
    idMap = response_payload[0]
    verifyPlaylistEntryAdded(self, host_id, idMap, lib_song_id, playlist_id)

class PlaylistEntryMultiAddTest(DoesServerOpsTestCase):
  def testAddPlaylistEntries(self):
    playlist_id = 1

    host_id1 = 1
    lib_song_id1 = 6
    host_id2 = 2
    lib_song_id2 = 7

    payload = '{"to_add" : ['+ str(lib_song_id1) + \
      ','+ str(lib_song_id2) +'],' +\
      '"id_maps" : [{"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id1) + '},' + \
      '{"server_id" : -1 , ' + \
      '"client_id" : ' + str(host_id2) + '}]}'
  
    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/playlists/'+str(playlist_id)+'/songs',
      payload)
    self.assertEqual(response.status_code, 201, msg=response.content)
    response_payload = json.loads(response.content)
    idMap = response_payload[0]
    verifyPlaylistEntryAdded(self, host_id1, idMap, lib_song_id1, playlist_id)
    idMap = response_payload[1]
    verifyPlaylistEntryAdded(self, host_id2, idMap, lib_song_id2, playlist_id)

class PlaylistEntryRemoveTestCase(DoesServerOpsTestCase):
  def testPlaylistDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/playlists/1/songs/1')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      len(PlaylistEntry.objects.filter(server_playlist_entry_id=1)),0)

