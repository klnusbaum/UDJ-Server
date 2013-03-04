import json

from udj.models import Library, AssociatedLibrary
from udj.models import Player
from udj.testhelpers.tests07.testclasses import KurtisTestCase
from udj.headers import FORBIDDEN_REASON_HEADER


class DefaultOwnerAdminTests(KurtisTestCase):

  def testGetEnabledLibraries(self):
    response = self.doGet('/players/1/enabled_libraries')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    returned_libraries = json.loads(response.content)
    actual_libraries = Player.objects.get(pk=1).EnabledLibraries
    self.assertEqual(len(actual_libraries), len(returned_libraries))
    for returned_library in returned_libraries:
      actual_library = actual_libraries.get(pk=returned_library['id'])
      self.assertEqual(actual_library.name, returned_library['name'])
      self.assertEqual(actual_library.description, returned_library['description'])
      self.assertEqual(actual_library.pub_key, returned_library['pub_key'])
      self.assertEqual(actual_library.get_read_permission_display(),
                       returned_library['read_permission'])
      self.assertEqual(actual_library.get_write_permission_display(),
                       returned_library['write_permission'])


  def testEnableGoodLibrary(self):
    response = self.doPut('/players/1/enabled_libraries/8')
    self.assertEqual(200, response.status_code)
    self.assertTrue(
        AssociatedLibrary.objects.filter(player__id=1, library__id=8, enabled=True).exists())


  def testEnableUnauthorizedLibrary(self):
    response = self.doPut('/players/1/enabled_libraries/9')
    self.assertEqual(403, response.status_code)
    self.assertEqual('library-permission', response[FORBIDDEN_REASON_HEADER])


"""
class OwnerAdministrationTests(udj.testhelpers.tests06.testclasses.BasicPlayerAdministrationTests):
  username = "kurtis"
  userpass = "testkurtis"

class AdminAdministrationTests(udj.testhelpers.tests06.testclasses.BasicPlayerAdministrationTests):
  username = "lucas"
  userpass = "testlucas"

class OwnerPasswordAdministrationTests(udj.testhelpers.tests06.testclasses.PasswordAdministrationTests):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminPasswordAdministrationTests(udj.testhelpers.tests06.testclasses.PasswordAdministrationTests):
  username = 'kurtis'
  userpass = 'testkurtis'
"""
