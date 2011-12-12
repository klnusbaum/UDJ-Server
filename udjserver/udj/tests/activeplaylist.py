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

class GetActivePlaylistTest(User2TestCase):
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
    request_id = 4
    payload = [{ 'lib_id' : 10, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    json_response = json.loads(response.content)
    added_entries = json_response['added_entries']
    request_ids = json_response['request_ids']
    already_played = json_response['already_played']

    response_entry = added_entries[0]

    self.assertEqual(len(already_played), 0)
    self.assertEqual(len(added_entries), 1)
    self.assertEqual(len(request_ids), 1)

    self.assertEqual(request_ids[0], request_id)

    self.assertEqual(UpVote.objects.filter(
      playlist_entry__adder__id=2, 
      playlist_entry__event__id=1, 
      playlist_entry__client_request_id=4).count(),
      1)
    self.assertFalse(DownVote.objects.filter(
      playlist_entry__adder__id=2, 
      playlist_entry__event__id=1, 
      playlist_entry__client_request_id=4).exists())

    addedEntry = ActivePlaylistEntry.objects.get(
      adder__id=2,  
      event__id=1,
      client_request_id=4)
    
    self.assertEqual(response_entry['id'], addedEntry.id) 
    self.assertEqual(
      response_entry['lib_song_id'], 
      addedEntry.song.host_lib_song_id)
    self.assertEqual(response_entry['song'], addedEntry.song.song) 
    self.assertEqual(response_entry['artist'], addedEntry.song.artist) 
    self.assertEqual(response_entry['album'], addedEntry.song.album) 
    self.assertEqual(response_entry['duration'], addedEntry.song.duration) 
    self.assertEqual(response_entry['up_votes'], 1) 
    self.assertEqual(response_entry['down_votes'], 0) 
    self.assertEqual(
      datetime.strptime(response_entry['time_added'], "%Y-%m-%dT%H:%M:%S"),
      addedEntry.time_added.replace(microsecond=0))
    self.assertEqual(response_entry['adder_id'], addedEntry.adder.id) 

  def testDuplicateAdd(self):
    request_id = 3
    payload = [{ 'lib_id' : 20, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
       
    songRequests = ActivePlaylistEntry.objects.filter(
      song__host_lib_song_id=20, client_request_id=3,event__id=1)
    self.assertEqual(len(songRequests), 1)

    alreadyAddedSong = songRequests[0] 

    response_json = json.loads(response.content)
    self.assertEqual(len(response_json['added_entries']), 1)
    self.assertEqual(len(response_json['request_ids']), 1)
    self.assertEqual(len(response_json['already_played']), 0)

    self.assertEqual(response_json['request_ids'][0], request_id)

    response_entry = response_json['added_entries'][0]
    addedEntry = ActivePlaylistEntry.objects.get(
      adder__id=2,  
      event__id=1,
      client_request_id=3)

    numUpvotes = UpVote.objects.filter(
      playlist_entry__adder__id=2, 
      playlist_entry__event__id=1, 
      playlist_entry__client_request_id=3).count()

    numDownvotes = DownVote.objects.filter(
      playlist_entry__adder__id=2, 
      playlist_entry__event__id=1, 
      playlist_entry__client_request_id=3).count()

    self.assertEqual(response_entry['id'], addedEntry.id) 
    self.assertEqual(
      response_entry['lib_song_id'], 
      addedEntry.song.host_lib_song_id)
    self.assertEqual(response_entry['song'], addedEntry.song.song) 
    self.assertEqual(response_entry['artist'], addedEntry.song.artist) 
    self.assertEqual(response_entry['album'], addedEntry.song.album) 
    self.assertEqual(response_entry['duration'], addedEntry.song.duration) 
    self.assertEqual(response_entry['up_votes'], numUpvotes) 
    self.assertEqual(response_entry['down_votes'], numDownvotes) 
    self.assertEqual(
      datetime.strptime(response_entry['time_added'], "%Y-%m-%dT%H:%M:%S"),
      addedEntry.time_added.replace(microsecond=0))
    self.assertEqual(response_entry['adder_id'], addedEntry.adder.id) 

  def testAlreadyPlayed1(self):
    request_id = 1
    payload = [{ 'lib_id' : 19, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    json_content = json.loads(response.content)
    added_entries = json_content['added_entries']    
    request_ids = json_content['request_ids']    
    already_played = json_content['already_played']
    self.assertEqual(len(added_entries), 0)
    self.assertEqual(len(request_ids), 0)
    self.assertEqual(len(already_played), 1)
    self.assertEqual(already_played[0], request_id)
    
    songThatShouldntBeThere = ActivePlaylistEntry.objects.filter(
      adder__id=3,
      event__id=1,
      song__host_lib_song_id=19)
    self.assertFalse(songThatShouldntBeThere.exists())
  


class AddSongToPlaylist2Tests(User2TestCase):
  def testAlreadyPlayed2(self):
    request_id = 1
    payload = [{ 'lib_id' : 21, 'client_request_id' : request_id}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    json_content = json.loads(response.content)
    added_entries = json_content['added_entries']    
    request_ids = json_content['request_ids']    
    already_played = json_content['already_played']
    self.assertEqual(len(added_entries), 0)
    self.assertEqual(len(request_ids), 0)
    self.assertEqual(len(already_played), 1)
    self.assertEqual(already_played[0], request_id)
    
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
    DeletedPlaylistEntry.objects.get(original_id=3)
    self.assertFalse(ActivePlaylistEntry.objects.filter(pk=3).exists())

  def testDuplicateRemove(self):
    response = self.doDelete('/udj/events/1/active_playlist/7')
    self.assertEqual(response.status_code, 200)
