import json
from udj.testhelpers.tests06.testclasses import KurtisTestCase

class ServerCapabilities(KurtisTestCase):

  def testGetSortingAlgos(self):
    response = self.doGet('/udj/0_6/sorting_algorithms')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    sortingAlgo = json.loads(response.content)
    self.assertEqual(3, len(sortingAlgo))
    firstAlgo = sortingAlgo[0]
    self.assertTrue('id' in firstAlgo)
    self.assertTrue('name' in firstAlgo)
    self.assertTrue('description' in firstAlgo)


  def testGetExternalLibs(self):
    response = self.doGet('/udj/0_6/external_libraries')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    externalLibs = json.loads(response.content)
    self.assertEqual(1, len(externalLibs))
    self.assertEqual('1', externalLibs[0]['id'])
    self.assertEqual(u'Rdio', externalLibs[0]['name'])
    self.assertEqual(u"A streaming music library with a butt load of music. They're also awesome.", externalLibs[0]['description'])
