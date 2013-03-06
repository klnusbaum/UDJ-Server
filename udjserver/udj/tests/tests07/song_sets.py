class GetSongSetTests(JeffTestCase):

  def testGetSongSets(self):
    response = self.doGet('/players/1/song_sets')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songsets = json.loads(response.content)
    self.assertEqual(2, len(songsets))
    expectedNames = ['Third Eye Blind', 'Mars Volta']
    for songset in songsets:
      self.assertTrue(songset['name'] in expectedNames)
      expectedSongs = SongSet.objects.get(name=songset['name'], player__id=1).Songs()
      expectedSongIds = [x.song.lib_id for x in expectedSongs]
      self.assertTrue(len(expectedSongIds), len(songset['songs']))
      for song in songset['songs']:
        self.assertTrue(song['id'] in expectedSongIds)


