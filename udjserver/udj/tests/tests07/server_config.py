import json
from udj.testhelpers.tests07.testclasses import KurtisTestCase

class ServerCapabilities(KurtisTestCase):

  def testGetSortingAlgos(self):
    response = self.doGet('/sorting_algorithms')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    sortingAlgo = json.loads(response.content)
    self.assertEqual(3, len(sortingAlgo))
    firstAlgo = sortingAlgo[0]
    self.assertTrue('id' in firstAlgo)
    self.assertTrue('name' in firstAlgo)
    self.assertTrue('description' in firstAlgo)

