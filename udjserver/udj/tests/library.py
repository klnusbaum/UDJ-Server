import json
from udj.tests.testhelpers import User2TestCase
from udj.tests.testhelpers import User3TestCase
from udj.tests.testhelpers import User4TestCase
from udj.models import LibraryEntry

def verifySongAdded(testObject, lib_id, ids, title, artist, album):
  matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, 
    owning_user=testObject.user_id)
  testObject.assertEqual(len(matchedEntries), 1, 
    msg="Couldn't find inserted song.")
  insertedLibEntry = matchedEntries[0]
  testObject.assertEqual(insertedLibEntry.title, title)
  testObject.assertEqual(insertedLibEntry.artist, artist)
  testObject.assertEqual(insertedLibEntry.album, album)

  testObject.assertTrue(lib_id in ids)


class LibAddTestCase(User2TestCase):
  def testSingleLibAdd(self):

    lib_id = 13
    title = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    duration = 451

    payload = [{
      'id' : lib_id,
      'title' : title,
      'artist' : artist,
      'album' : album,
      'duration' : duration
    }]


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 201)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id, ids, title, artist, album)

  def testMultiLibAdd(self):

    lib_id1 = 13
    title1 = 'Roulette Dares'
    artist1 = 'The Mars Volta'
    album1 = 'Deloused in the Comatorium'
    duration1 = 451

    lib_id2 = 14
    title2 = 'Goliath'
    artist2 = 'The Mars Volta'
    album2 = 'The Bedlam in Goliath'
    duration2 = 435

    payload = [
      {
        'id' : lib_id1,
        'title' : title1,
        'artist' : artist1,
        'album' : album1,
        'duration' : duration1
      },
      {
        'id' : lib_id2,
        'title' : title2,
        'artist' : artist2,
        'album' : album2,
        'duration' : duration2
      }
    ]

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload))

    self.assertEqual(response.status_code, 201, msg=response.content)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    verifySongAdded(self, lib_id1, ids, title1, artist1, album1)
    verifySongAdded(self, lib_id2, ids, title2, artist2, album2)

  def testDupAdd(self):

    dup_lib_id=1

    payload = [{
      "song" : "Never Let You Go", 
      "artist" : "Third Eye Blind",
      "album" : "Blue", 
      "id" : dup_lib_id, 
      "duration" : 237 
    }]
    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload))

    self.assertEqual(response.status_code, 201, msg=response.content)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    self.assertEqual(ids[0], dup_lib_id)
    onlyOneSong = LibraryEntry.objects.get(
      owning_user__id=2, host_lib_song_id=dup_lib_id)
    
class LibRemoveTestCase(User2TestCase):
  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/10')
    self.assertEqual(response.status_code, 200)
    deletedEntries = LibraryEntry.objects.filter(
      host_lib_song_id=10, owning_user__id=2, is_deleted=True)
    self.assertEqual(len(deletedEntries), 1)

  def testFullDelete(self):
    response = self.doDelete('/udj/users/'+self.user_id+'/library')
    self.assertEqual(response.status_code, 200)
    deletedEntries = LibraryEntry.objects.filter(
      owning_user__id=2, is_deleted=True)
    self.assertEqual(len(deletedEntries), 12)

