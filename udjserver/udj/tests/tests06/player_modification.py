import json
from udj import player_mod_test_helpers
from udj.models import Player, PlayerPassword
from udj.tests.tests06.testhelpers import AlejandroTestCase
from udj.headers import MISSING_RESOURCE_HEADER
from udj.views.views06.auth import hashPlayerPassword

class OwnerModificationTests(player_mod_test_helpers.BasicPlayerModificationTests):
  username = "kurtis"
  userpass = "testkurtis"


class AdminModificationTests(player_mod_test_helpers.BasicPlayerModificationTests):
  username = "lucas"
  userpass = "testlucas"



class PlayerModificationTests2(AlejandroTestCase):

  def testChangePassword(self):
    oldTime = PlayerPassword.objects.get(player__id=3).time_set
    newPassword = "nudepassword"
    response = self.doPost('/udj/0_6/players/3/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=3)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))
    self.assertTrue(oldTime < playerPassword.time_set)

  def testDeletePassword(self):
    response = self.doDelete('/udj/0_6/players/3/password')
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.filter(player__id=3)
    self.assertFalse(playerPassword.exists())

