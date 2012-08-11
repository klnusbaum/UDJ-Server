import json
import udj
from udj.models import Player, LibraryEntry, ActivePlaylistEntry, Participant
from datetime import datetime

class GetActivePlaylistTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  def testGetPlaylist(self):

    response = self.doGet('/udj/0_6/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    realCurrentSong = ActivePlaylistEntry.objects.get(song__player__id=1, state='PL')
    self.assertEqual(current_song['song']['id'], realCurrentSong.song.player_lib_song_id)
    plSongs = ActivePlaylistEntry.objects.filter(song__player__id=1, state='QE')
    plSongIds = [x.song.player_lib_song_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))

    self.assertEqual(jsonResponse['volume'], 5)
    self.assertEqual(jsonResponse['state'], 'playing')

class OwnerPlaylistModTests(udj.testhelpers.tests06.testclasses.PlaylistModTests):
  username='kurtis'
  userpass='testkurtis'

class AdminPlaylistModTests(udj.testhelpers.tests06.testclasses.PlaylistModTests):
  username="lucas"
  userpass="testlucas"

  def setUp(self):
    super(udj.testhelpers.tests06.testclasses.PlaylistModTests, self).setUp()
    lucas = Participant.objects.get(user__id=5, player__id=1)
    lucas.time_last_interaction = datetime.now()
    lucas.save()
    self.oldtime = lucas.time_last_interaction


  def tearDown(self):
    lucas = Participant.objects.get(user__id=5, player__id=1)
    self.assertTrue(lucas.time_last_interaction > self.oldtime)

