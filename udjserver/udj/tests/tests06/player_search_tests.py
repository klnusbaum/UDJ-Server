import json

from udj.tests.tests05.testhelpers import JeffTestCase

from settings import min_search_radius, max_search_radius

class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/udj/0_6/players/40.11241/-88.222053')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

  def testGetPlayersByName(self):
    response = self.doGet('/udj/0_6/players?name=kurtis')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

  def testTooSmallRadius(self):
    badRadius = min_search_radius -1
    response = self.doGet('/udj/0_6/players/40.11381/-88.224083?radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
    radiiInfo = json.loads(response.content)
    self.assertEqual(min_search_radius, radiiInfo['min_radius'])
    self.assertEqual(max_search_radius, radiiInfo['max_radius'])

  def testTooBigRadius(self):
    badRadius = max_search_radius +1
    response = self.doGet('/udj/0_6/players/40.11381/-88.224083?radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
    radiiInfo = json.loads(response.content)
    self.assertEqual(min_search_radius, radiiInfo['min_radius'])
    self.assertEqual(max_search_radius, radiiInfo['max_radius'])

