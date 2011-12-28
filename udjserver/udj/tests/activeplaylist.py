import json
from datetime import datetime
from udj.tests import User2TestCase
from udj.tests import User3TestCase
from udj.tests import User5TestCase
from udj.models import UpVote
from udj.models import DownVote
from udj.models import ActivePlaylistEntry

class GetActivePlaylistTest(User3TestCase):
  def testGetPlaylist(self):
    response = self.doGet('/udj/events/2/active_playlist')
    self.assertEqual(response.status_code, 200)
    playlist = json.loads(response.content)
    self.assertEqual(len(playlist), 4)
    self.assertEqual(playlist[0]['id'], 1)
    self.assertEqual(playlist[1]['id'], 2)
    self.assertEqual(playlist[2]['id'], 3)
    self.assertEqual(playlist[3]['id'], 4)

class AddSongToPlaylistTests(User2TestCase):

  def testSimpleAdd(self):
    request_id = 6
    payload = [{ 'lib_id' : 2, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)

    entry = ActivePlaylistEntry.objects.get(adder__id=2, event__id=2, 
      client_request_id=request_id)
    upvotes = UpVote.objects.filter(
      playlist_entry__client_request_id=request_id,
      playlist_entry__event__id=2,
      user__id=2)
    self.assertEqual(upvotes.count(),  1)
    downvotes = DownVote.objects.filter(
      playlist_entry__client_request_id=request_id,
      playlist_entry__event__id=2,
      user__id=2)
    self.assertEqual(downvotes.count(), 0)
    addedEntry = ActivePlaylistEntry.objects.get(
      adder__id=2,  
      event__id=2,
      client_request_id=request_id)
    
  def testDuplicateAdd(self):
    request_id = 2
    payload = [{ 'lib_id' : 1, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
       
    songRequests = ActivePlaylistEntry.objects.get(
      song__host_lib_song_id=1, client_request_id=request_id, event__id=2)

  def testAlreadyIsPlaying(self):
    request_id = 1
    payload = [{ 'lib_id' : 4, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=2,
      event__id=2,
      client_request_id=request_id,
      state=u'QE')
    self.assertFalse(songThatShouldntBeThere.exists())

  def testAddedAndDeleted(self):
    request_id = 5
    payload = [{ 'lib_id' : 12 , 'client_request_id' : request_id}]

    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=2,
      event__id=2,
      client_request_id=request_id,
      state=u'QE')
    self.assertFalse(songThatShouldntBeThere.exists())

class AddSongToPlaylist2Tests(User2TestCase):
  def testAlreadyPlayed(self):
    request_id = 1
    payload = [{ 'lib_id' : 11, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=2,
      event__id=2,
      client_request_id=request_id,
      state=u'QE')
    self.assertFalse(songThatShouldntBeThere.exists())

class TestVoting(User5TestCase):

  def setUp(self):
    super(TestVoting, self).setUp()  
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)

  def testUpVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = UpVote.objects.get(playlist_entry__id=playlist_id, user__id=5)

  def testDownVote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    downvote = DownVote.objects.get(playlist_entry__id=playlist_id, user__id=5)

  def testDoubleUpVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost('/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 403)

  def testDoubleDownVote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 403)
"""

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

class TestGetAddRequests(User1TestCase):
  def testGetAddRequests(self):
    response = self.doGet('/udj/events/1/active_playlist/users/2/add_requests')
    self.assertEqual(response.status_code, 200)
    #TODO make this test more rigerous
    returnedRequests = json.loads(response.content)
    self.assertEqual(len(returnedRequests),4) 

class TestGetAddRequests2(User2TestCase):
  def testGetAddRequests(self):
    response = self.doPut('/udj/events/1/users/3')
    self.assertEqual(response.status_code, 201)
    response = self.doGet('/udj/events/1/active_playlist/users/3/add_requests')
    self.assertEqual(response.status_code, 200)
    #TODO make this test more rigerous
    returnedRequests = json.loads(response.content)
    self.assertEqual(len(returnedRequests),3) 

class TestGetVotes(User1TestCase):
  def testGetVotes(self):
    response = self.doGet('/udj/events/1/active_playlist/users/2/votes')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    upvotes = jsonResponse['up_vote_ids']
    downvotes = jsonResponse['down_vote_ids']
    self.assertEqual(len(upvotes), 3)
    self.assertEqual(len(downvotes), 0)
    requiredUpvotes = [6,5,3]
    for upvote in requiredUpvotes:
      self.assertTrue(upvote in upvotes)

class TestGetVotes2(User2TestCase):
  def testGetVotes2(self):
    response = self.doPut('/udj/events/1/users/3')
    self.assertEqual(response.status_code, 201)
    response = self.doGet('/udj/events/1/active_playlist/users/3/votes')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    upvotes = jsonResponse['up_vote_ids']
    downvotes = jsonResponse['down_vote_ids']
    self.assertEqual(len(upvotes), 3)
    self.assertEqual(len(downvotes), 1)
    requiredUpvotes = [5,4,3]
    for upvote in requiredUpvotes:
      self.assertTrue(upvote in upvotes)
    self.assertTrue(6 in downvotes)
"""
