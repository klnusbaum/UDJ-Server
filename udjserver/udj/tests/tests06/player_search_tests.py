import json
from udj.tests.tests05.testhelpers import JeffTestCase

class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/udj/players/40.11241/-88.222053')
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
    response = self.doGet('/udj/players?name=kurtis')
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


