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



class OwnerPasswordModificationTests(player_mod_test_helpers.PasswordModificationTests):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminPasswordModificationTests(player_mod_test_helpers.PasswordModificationTests):
  username = 'kurtis'
  userpass = 'testkurtis'
