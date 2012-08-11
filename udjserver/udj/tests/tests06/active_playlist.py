import json
import udj
from udj.models import Player, LibraryEntry, ActivePlaylistEntry

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
