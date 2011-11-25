import json
from udj.tests import User2TestCase

class GetActivePlaylistTest(User2TestCase):
  def testGetPlaylist(self):
    response = self.doGet('/udj/events/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    playlist = json.loads(response.content)
    self.assertEqual(len(playlist), 4)
"""
    self.assertEqual(playlist[0]['id'] = 
    self.assertEqual(playlist[1]['id'] = 2
"""

