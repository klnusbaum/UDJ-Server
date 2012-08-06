import json

from udj.testhelpers.tests06.testclasses import JeffTestCase

from settings import min_search_radius, max_search_radius

class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/udj/0_6/players/40.11241/-88.222053')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 3)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])
    location = firstPlayer['location']
    self.assertEqual("201 N Goodwin", location['address'])
    self.assertEqual("Urbana", location['locality'])
    self.assertEqual("IL", location['region'])
    self.assertEqual("61801", location['postal_code'])
    self.assertEqual("US", location['country'])


  def testGetPlayersByName(self):
    response = self.doGet('/udj/0_6/players?name=kurtis')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 2)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

  def testLocationSearchWithLimit(self):
    response = self.doGet('/udj/0_6/players/40.11241/-88.222053?max_results=1')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)

  def testNameSearchWithLimit(self):
    response = self.doGet('/udj/0_6/players?name=kurtis&max_results=1')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)

  def testSearchWithRadius(self):
    response = self.doGet('/udj/0_6/players/40.111595/-88.204847?radius=2')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(2, len(players))

  def testSearchWithRadiusAndLimit(self):
    response = self.doGet('/udj/0_6/players/40.111595/-88.204847?radius=2&max_results=1')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(1, len(players))
    self.assertEqual(6, players[0]["id"])

  def testTooSmallRadius(self):
    badRadius = min_search_radius -1
    response = self.doGet('/udj/0_6/players/40.11241/-88.222053?radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
    self.isJSONResponse(response)
    radiiInfo = json.loads(response.content)
    self.assertEqual(min_search_radius, radiiInfo['min_radius'])
    self.assertEqual(max_search_radius, radiiInfo['max_radius'])

  def testTooBigRadius(self):
    badRadius = max_search_radius +1
    response = self.doGet('/udj/0_6/players/40.11381/-88.224083?radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
    self.isJSONResponse(response)
    radiiInfo = json.loads(response.content)
    self.assertEqual(min_search_radius, radiiInfo['min_radius'])
    self.assertEqual(max_search_radius, radiiInfo['max_radius'])

