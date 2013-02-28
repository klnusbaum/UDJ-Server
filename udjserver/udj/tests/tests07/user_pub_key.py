import json

from udj.models import UserPubKey
from udj.testhelpers.tests07.testclasses import JeffTestCase
from udj.headers import MISSING_RESOURCE_HEADER

class UserPubKeyTests(JeffTestCase):

  def testGetOthersKey(self):
    response = self.doGet('/2/public_key')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    parsedResponse = json.loads(response.content)
    self.assertEqual(UserPubKey.objects.get(user__id=2).pub_key, parsedResponse['key'])

  def testGetNonExistentKey(self):
    response = self.doGet('/4/public_key')
    self.assertEqual(404, response.status_code)
    self.assertEqual('public-key', response[MISSING_RESOURCE_HEADER])

  def testGetKeyForBadUser(self):
    response = self.doGet('/19938849/public_key')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])
