import json
from udj.testhelpers.tests07.testclasses import KurtisTestCase
from settings import MIN_SEARCH_RADIUS, MAX_SEARCH_RADIUS, DEFAULT_PLAYER_PERMISSIONS
from udj.models import PlayerPermission

class ServerConfigTests(KurtisTestCase):

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

  def testGetSearchRadii(self):
    response = self.doGet('/player_search_radius')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    received_json = json.loads(response.content)
    self.assertEqual(MAX_SEARCH_RADIUS, received_json['max_radius'])
    self.assertEqual(MIN_SEARCH_RADIUS, received_json['min_radius'])

  def testGetDefaultPlayerPermissions(self):
    expected_permissions = map(lambda x: PlayerPermission.PERMISSION_CODE_MAP[x],
                               DEFAULT_PLAYER_PERMISSIONS)
    response = self.doGet('/default_player_permissions')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    received_json = json.loads(response.content)
    self.assertEqual(len(expected_permissions), len(received_json))
    for perm in expected_permissions:
      self.assertTrue(perm in received_json)
