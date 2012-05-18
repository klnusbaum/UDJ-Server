import json
from udj.models import LibraryEntry
from udj.tests.testhelpers import KurtisTestCase
from udj.headers import MISSING_RESOURCE_HEADER

class LibTestCases(KurtisTestCase):

  def verifySongAdded(self, jsonSong):
    addedSong = LibraryEntry.objects.get(player__id=1, player_lib_song_id=jsonSong['id'])
    self.assertEqual(addedSong.title, jsonSong['title'])
    self.assertEqual(addedSong.artist, jsonSong['artist'])
    self.assertEqual(addedSong.album, jsonSong['album'])
    self.assertEqual(addedSong.track, jsonSong['track'])
    self.assertEqual(addedSong.genre, jsonSong['genre'])
    self.assertEqual(addedSong.duration, jsonSong['duration'])

  def testSimpleAdd(self):
    payload = [{
      "id" : 11,
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }]

    response = self.doJSONPut('/udj/users/2/players/1/library/songs', json.dumps(payload))
    self.assertEqual(201, response.status_code, response.content)
    self.verifySongAdded(payload[0])


  def testDuplicateAdd(self):
    payload = [{
      "id" : 10,
      "title" : "My Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skirllex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }]

    response = self.doJSONPut('/udj/users/2/players/1/library/songs', json.dumps(payload))
    self.assertEqual(409, response.status_code, response.content)

  def testDelete(self):
    response = self.doDelete('/udj/users/2/players/1/library/10')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(True, LibraryEntry.objects.get(player__id=1, player_lib_song_id=10).is_deleted)

  def testBadDelete(self):
    response = self.doDelete('/udj/users/2/players/1/library/12')
    self.assertEqual(404, response.status_code, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  def testAddSong2BanList(self):
    response = self.doPut('/udj/users/2/players/1/ban_music/1')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(LibraryEntry.objects.get(player__id=1, player_lib_song_id=1).is_banned, True)

  def testUnbanSong(self):
    response = self.doDelete('/udj/users/2/players/1/ban_music/4')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(LibraryEntry.objects.get(player__id=1, player_lib_song_id=4).is_banned, False)

  def testBadSongBan(self):
    response = self.doDelete('/udj/users/2/players/1/ban_music/12')
    self.assertEqual(404, response.status_code, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  def testMultiMod(self):
    to_add = [{
      "id" : 11,
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }]

    to_delete = [1,2]

    response = self.doPost('/udj/users/2/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(200, response.status_code, response.content)
    self.verifySongAdded(to_add[0])
    self.assertEqual(True, LibraryEntry.objects.get(player__id=1, player_lib_song_id=1).is_deleted)
    self.assertEqual(True, LibraryEntry.objects.get(player__id=1, player_lib_song_id=2).is_deleted)

  def testBadMultiModAdd(self):
    to_add = [{
      "id": 1,
      "title": "Semi-Charmed Life",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 3,
      "genre": "Rock",
      "duration": 268
    },
    {
      "id": 2,
      "title": "Narcolepsy",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 2,
      "genre": "Rock",
      "duration": 228,
    },
    {
      "id": 11,
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    } 
    ]
    to_delete=[]
    response = self.doPost('/udj/users/2/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(409, response.status_code, response.content)
    jsonResponse = json.loads(response.content)
    self.assertEqual([1,2], jsonResponse)
    #Make sure we didn't add fuel because this was a bad one
    self.assertFalse(LibraryEntry.objects.filter(player__id=1, player_lib_song_id=11).exists())

