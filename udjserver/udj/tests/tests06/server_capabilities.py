import json
from udj.testhelpers.tests06.testclasses import KurtisTestCase

class ServerCapabilities(KurtisTestCase):

  def testGetSortingAlgos(self):
    response = self.doGet('/udj/0_6/sorting_algorithms')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    sortingAlgo = json.loads(response.content)
    self.assertEqual(1, len(sortingAlgo))
    self.assertEqual('1', sortingAlgo[0]['id'])
    self.assertEqual(u'Total Votes', sortingAlgo[0]['name'])
    self.assertEqual(u'Sorts the playlist be calculating each songs total votes (upvotes - downvotes). Ties are broken by the time each song was added (with preference given to the song that was added first', sortingAlgo[0]['description'])

  def testGetExternalLibs(self):
    response = self.doGet('/udj/0_6/external_libraries')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    externalLibs = json.loads(response.content)
    self.assertEqual(1, len(externalLibs))
    self.assertEqual('1', externalLibs[0]['id'])
    self.assertEqual(u'Spotify', externalLibs[0]['name'])
    self.assertEqual(u'A streaming music library with a butt load of music', externalLibs[0]['description'])
