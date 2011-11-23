import json
from udj.tests.testcases import User1TestCase
from udj.tests.testcases import User2TestCase
from udj.tests.testcases import User3TestCase
from udj.models import LibraryEntry

def verifySongAdded(testObject, lib_id, ids, song, artist, album):
  matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, 
    owning_user=testObject.user_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted song.")
  insertedLibEntry = matchedEntries[0]
  testObject.assertEqual(insertedLibEntry.song, song)
  testObject.assertEqual(insertedLibEntry.artist, artist)
  testObject.assertEqual(insertedLibEntry.album, album)

  testObject.assertTrue(lib_id in ids)


class LibSingleAddTestCase(User1TestCase):
  def testLibAdd(self):

    lib_id = 1
    song = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    payload = '[{' + \
     '"id" : ' + str(lib_id) + ',' +\
     '"song" : "' + song + '",'+\
     '"artist" : "' + artist +'",'+\
     '"album" : "' + album + '"}]'


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)
    self.assertEqual(response.status_code, 201)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id, ids, song, artist, album)


class LibMultiAddTestCase(User1TestCase):
  def testLibAdds(self):

    lib_id1 = 1
    song1 = 'Roulette Dares'
    artist1 = 'The Mars Volta'
    album1 = 'Deloused in the Comatorium'

    lib_id2 = 2
    song2 = 'Ilyena'
    artist2 = 'The Mars Volta'
    album2 = 'The Bedlam in Goliath'

    payload = '[{' + \
      '"id" : ' + str(lib_id1) + ',' + \
      '"song" : "' + song1 + '",' + \
      '"artist" : "' + artist1 + '",' + \
      '"album" : "' + album1 + '"},{' + \
      '"id" : ' + str(lib_id2) + ',' + \
      '"song" : "' + song2 + '",' + \
      '"artist" : "' + artist2 + '",' + \
      '"album" : "' + album2 + '"}]'


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', payload)

    self.assertEqual(response.status_code, 201, msg=response.content)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id1, ids, song1, artist1, album1)
    verifySongAdded(self, lib_id2, ids, song2, artist2, album2)

class LibTestDuplicateAdd(User1TestCase):
  def testDupAdd(self):

    payload = []
    payload.append({"song" : "Deep Inside Of You", "artist" : "Third Eye Blind",
      "albumt" : "Blue", "id" : 10})
    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload))

    self.assertEqual(response.status_code, 201, msg=response.content)
    ids = json.loads(response.content)
    self.assertEqual(ids[0], 10)
    self.assertEqual(len(LibraryEntry.objects.filter(owning_user__id=2, host_lib_song_id=10)), 1)
    
class LibRemoveTestCase(User1TestCase):
  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/10')
    self.assertEqual(response.status_code, 200)
    deletedEntries = LibraryEntry.objects.filter(
      host_lib_song_id=10, owning_user__id=2, is_deleted=True)
    self.assertEqual(len(deletedEntries), 1)


class LibFullDeleteTest(User1TestCase):
  def testFullDelete(self):
    response = self.doDelete('/udj/users/'+self.user_id+'/library')
    self.assertEqual(response.status_code, 200)
    deletedEntries = LibraryEntry.objects.filter(
      owning_user__id=2, is_deleted=True)
    self.assertEqual(len(deletedEntries), 13)

