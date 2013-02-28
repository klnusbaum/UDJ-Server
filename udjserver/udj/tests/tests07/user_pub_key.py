import json

from udj.models import UserPubKey
from udj.testhelpers.tests07.testclasses import JeffTestCase

class UserPubKeyTests(JeffTestCase):

  def testGetOthersKey(self):
    response = self.doGet('/2/public_key')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    parsedResponse = json.loads(response.content)
    self.assertEqual(UserPubKey.objects.get(user__id=2).pub_key, parsedResponse['key'])


