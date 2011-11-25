import json
from udj.tests import User2TestCase
from udj.tests import User1TestCase

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
    payload = [{ 'lib_id' : 10, 'client_request_id' : 4}]
    response = \
      self.doJSONPut('/udj/events/1/active_playlist/songs', json.dumps(payload))
    self.assertEqual(response.status_code, 200)
