import json
from datetime import datetime
from udj.tests import User2TestCase
from udj.tests import User3TestCase
from udj.tests import User4TestCase
from udj.tests import User5TestCase
from udj.models import ActivePlaylistEntry
from udj.models import Vote
from udj.models import PlaylistEntryTimePlayed

class GetActivePlaylistTest(User3TestCase):

  def testGetPlaylist(self):
    response = self.doGet('/udj/events/2/active_playlist')
    self.assertEqual(response.status_code, 200)

    responseContent = json.loads(response.content)

    playlist = responseContent['active_playlist']
    self.assertEqual(len(playlist), 4)

    self.assertEqual(playlist[0]['id'], 1)
    self.assertEqual(playlist[0]['up_votes'], 2) 
    self.assertEqual(playlist[0]['down_votes'], 0) 

    self.assertEqual(playlist[1]['id'], 2)
    self.assertEqual(playlist[1]['up_votes'], 1) 
    self.assertEqual(playlist[1]['down_votes'], 0) 

    self.assertEqual(playlist[2]['id'], 4)
    self.assertEqual(playlist[2]['up_votes'], 1)
    self.assertEqual(playlist[2]['down_votes'], 0)

    self.assertEqual(playlist[3]['id'], 3)
    self.assertEqual(playlist[3]['up_votes'], 1)
    self.assertEqual(playlist[3]['down_votes'], 1)

    result = responseContent['current_song']
    actualCurrentSong = ActivePlaylistEntry.objects.filter(
      event__id=2, state=u'PL')[0]
    self.assertEqual(
      actualCurrentSong.song.host_lib_song_id, result['lib_song_id'])
    self.assertEqual(actualCurrentSong.song.title, result['title'])
    self.assertEqual(actualCurrentSong.song.artist, result['artist'])
    self.assertEqual(actualCurrentSong.song.album, result['album'])
    self.assertEqual(actualCurrentSong.song.duration, result['duration'])
    self.assertEqual(
      Vote.objects.filter(playlist_entry=actualCurrentSong, weight=1).count(),
      result['up_votes'])
    self.assertEqual(
      Vote.objects.filter(playlist_entry=actualCurrentSong, weight=-1).count(),
      result['down_votes'])
    self.assertEqual(
      actualCurrentSong.time_added, 
      datetime.strptime(result['time_added'], "%Y-%m-%dT%H:%M:%S"))
    self.assertEqual(PlaylistEntryTimePlayed.objects.get(
      playlist_entry=actualCurrentSong).time_played, 
      datetime.strptime(result['time_played'], "%Y-%m-%dT%H:%M:%S"))
    self.assertEqual(actualCurrentSong.adder.id, result['adder_id'])
    self.assertEqual(actualCurrentSong.adder.username, result['adder_username'])

class TestGetEmptyPlaylist(User4TestCase):
  def testGetEmptyPlaylist(self):
    response = self.doGet('/udj/events/3/active_playlist')
    self.assertEqual(response.status_code, 200, response.content)
    responseContent = json.loads(response.content)
    currentSong = responseContent['current_song']
    activePlaylist = responseContent['active_playlist']
    self.assertEqual(currentSong, {})
    self.assertEqual(activePlaylist, [])

class AddSongToPlaylistTests(User2TestCase):

  def testSimpleAdd(self):
    request_id = 6
    payload = [{ 'lib_id' : 2, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/2/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)

    entry = ActivePlaylistEntry.objects.get(adder__id=2, event__id=2, 
      client_request_id=request_id)
    upvotes = Vote.objects.filter(
      playlist_entry__client_request_id=request_id,
      playlist_entry__event__id=2,
      user__id=2,
      weight=1)
    self.assertEqual(upvotes.count(),  1)
    downvotes = Vote.objects.filter(
      playlist_entry__client_request_id=request_id,
      playlist_entry__event__id=2,
      user__id=2,
      weight=-1)
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
    upvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=1)

  def testDownVote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    downvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=-1)

  def testDoubleUpVote(self):
    playlist_id = 3
    response = self.doPost('/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost('/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=1)
    

  def testDoubleDownVote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=-1)

  def testUpVoteDownVote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=-1)

  def testDownvoteUpvote(self):
    playlist_id = 3
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/downvote', {})
    self.assertEqual(response.status_code, 200)
    response = self.doPost(
      '/udj/events/2/active_playlist/3/users/5/upvote', {})
    self.assertEqual(response.status_code, 200)
    upvote = Vote.objects.get(
      playlist_entry__id=playlist_id, user__id=5, weight=1)


class TestRemoveSong(User2TestCase):
  def testBasicRemove(self):
    playlist_id=3
    response = self.doDelete('/udj/events/2/active_playlist/songs/3')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      ActivePlaylistEntry.objects.get(id=3).state, u'RM')

  def testDuplicateRemove(self):
    response = self.doDelete('/udj/events/2/active_playlist/songs/7')
    self.assertEqual(response.status_code, 200)

class TestGetAddRequests(User2TestCase):
  def testGetAddRequests(self):
    response = self.doGet('/udj/events/2/active_playlist/users/2/add_requests')
    self.assertEqual(response.status_code, 200)
    #TODO make this test more rigerous
    returnedRequests = json.loads(response.content)
    self.assertEqual(len(returnedRequests),5) 

class TestGetVotes(User2TestCase):
  def testGetVotes(self):
    response = self.doGet('/udj/events/2/active_playlist/users/2/votes')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    upvotes = jsonResponse['up_vote_ids']
    downvotes = jsonResponse['down_vote_ids']
    self.assertEqual(len(upvotes), 2)
    self.assertEqual(len(downvotes), 0)
    requiredUpvotes = [1,3]
    for upvote in requiredUpvotes:
      self.assertTrue(upvote in upvotes)

class TestGetVotes2(User3TestCase):
  def testGetVotes2(self):
    response = self.doGet('/udj/events/2/active_playlist/users/3/votes')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    upvotes = jsonResponse['up_vote_ids']
    downvotes = jsonResponse['down_vote_ids']
    self.assertEqual(len(upvotes), 3)
    self.assertEqual(len(downvotes), 1)
    requiredUpvotes = [2,4,1]
    for upvote in requiredUpvotes:
      self.assertTrue(upvote in upvotes)
    self.assertTrue(3 in downvotes)
