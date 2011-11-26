import json
from datetime import datetime
from udj.tests import User2TestCase
from udj.tests import User1TestCase
from udj.models import UpVote
from udj.models import DownVote
from udj.models import ActivePlaylistEntry
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

  def testDoubleAdd(self):
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
