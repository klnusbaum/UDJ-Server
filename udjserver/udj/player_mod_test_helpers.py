import json
from udj.tests.tests06.testhelpers import DoesServerOpsTestCase
from udj.views.views06.auth import hashPlayerPassword
from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Player, PlayerPassword, PlayerLocation

class BasicPlayerModificationTests(DoesServerOpsTestCase):

  def testChangeName(self):
    newName = "A Bitchn' name"
    response = self.doPost('/udj/0_6/players/1/name', {'name': newName})
    self.assertEqual(200, response.status_code)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.name, newName)

  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/udj/0_6/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : 55447,
      'country' : 'U.S.'
    }

    response = self.doPost('/udj/0_6/players/1/location', newLocation)
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerLocation = PlayerLocation.objects.get(player__id=1)

  def testSetLocationWithNoPreviousLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : 55447,
      'country' : 'U.S.'
    }

    response = self.doPost('/udj/0_6/players/4/location', newLocation)
    self.assertEqual(200, response.status_code)
    playerLocation = PlayerLocation.objects.get(player__id=4)


