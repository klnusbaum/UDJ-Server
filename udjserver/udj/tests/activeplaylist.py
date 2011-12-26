import json
from datetime import datetime
from udj.tests import User2TestCase
from udj.tests import User1TestCase
from udj.tests import User3TestCase
from udj.models import UpVote
from udj.models import DownVote
from udj.models import ActivePlaylistEntry
from udj.models import DeletedPlaylistEntry
from udj.models import PlayedPlaylistEntry
from udj.models import CurrentSong

class GetActivePlaylistTest(User3TestCase):
  def testGetPlaylist(self):
    response = self.doGet('/udj/events/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    playlist = json.loads(response.content)
    self.assertEqual(len(playlist), 4)
    self.assertEqual(playlist[0]['id'], 5)
    self.assertEqual(playlist[1]['id'], 3)
    self.assertEqual(playlist[2]['id'], 4)
    self.assertEqual(playlist[3]['id'], 6)

class AddSongToPlaylistTests(User1TestCase):

  def testSimpleAdd(self):
    request_id = 5
    payload = [{ 'lib_id' : 10, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)

    entry = ActivePlaylistEntry.objects.get(adder__id=2, event__id=1, 
      client_request_id=request_id)
    self.assertEqual(UpVote.objects.filter(playlist_entry=entry.entry_id.id).count(), 1)
    self.assertFalse(DownVote.objects.filter(playlist_entry=entry.entry_id.id).exists())

    addedEntry = ActivePlaylistEntry.objects.get(
      adder__id=2,  
      event__id=1,
      client_request_id=request_id)
    
  def testDuplicateAdd(self):
    request_id = 3
    payload = [{ 'lib_id' : 20, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
       
    songRequests = ActivePlaylistEntry.objects.get(
      song__host_lib_song_id=20, client_request_id=request_id, event__id=1)

  def testAlreadyPlayed1(self):
    request_id = 1
    payload = [{ 'lib_id' : 19, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=2,
      event__id=1,
      client_request_id=request_id)
    self.assertFalse(songThatShouldntBeThere.exists())

  def testAddedAndDeleted(self):
    request_id = 4
    payload = [{ 'lib_id' : 20 , 'client_request_id' : request_id}]

    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=2,
      event__id=1,
      client_request_id=request_id)
    self.assertFalse(songThatShouldntBeThere.exists())

class AddSongToPlaylist2Tests(User2TestCase):
  def testAlreadyPlayed2(self):
    response = self.doPut('/udj/events/1/user')
    self.assertEqual(response.status_code, 201)
    request_id = 1
    payload = [{ 'lib_id' : 21, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=3,
      event__id=1,
      song__host_lib_song_id=21)
    self.assertFalse(songThatShouldntBeThere.exists())

class TestVoting(User3TestCase):
  def testUpVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/1/active_playlist/3/upvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = UpVote.objects.get(playlist_entry__id=playlist_id, user__id=4)

  def testDownVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/1/active_playlist/3/downvote', {})
    self.assertEqual(response.status_code, 200)
    downvote = DownVote.objects.get(playlist_entry__id=playlist_id, user__id=4)

  def testDoubleUpVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/1/active_playlist/3/upvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost('/udj/events/1/active_playlist/3/upvote', {})
    self.assertEqual(response.status_code, 403)

  def testDoubleDownVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/1/active_playlist/3/downvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost('/udj/events/1/active_playlist/3/downvote', {})
    self.assertEqual(response.status_code, 403)

class TestRemoveSong(User1TestCase):
  def testBasicRemove(self):
    playlist_id=3
    response = self.doDelete('/udj/events/1/active_playlist/3')
    self.assertEqual(response.status_code, 200)
    DeletedPlaylistEntry.objects.get(entry_id__id=3)
    self.assertFalse(ActivePlaylistEntry.objects.filter(pk=3).exists())

  def testDuplicateRemove(self):
    response = self.doDelete('/udj/events/1/active_playlist/7')
    self.assertEqual(response.status_code, 200)
