import json
from udj.models import LibraryEntry, ActivePlaylistEntry
from udj.tests.tests06.testhelpers import KurtisTestCase

class ServerCapabilities(KurtisTestCase):

  def testGetSortingAlgos(self):
    response = self.doGet('/udj/0_6/sorting_algorithms')
    self.assertEqual(200, response.status_code)
    self.assertEqual('text/json', response['Content-Type'])
    sortingAlgo = json.loads(response.content)
    self.assertEqual(1, len(sortingAlgo))
    self.assertEqual(1, sortingAlgo[0]['id'])
    self.assertEqual(u'Total Votes', sortingAlgo[0]['name'])
    self.assertEqual(u'Sorts the playlist be calculating each songs total votes (upvotes - downvotes). Ties are broken by the time each song was added (with preference given to the song that was added first', sortingAlgo[0]['description'])
