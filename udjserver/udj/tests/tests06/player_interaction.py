import json
from udj.models import Participant
from datetime import datetime
from udj.testhelpers.tests06.testclasses import LeeTestCase

class BeginParticipateTests(LeeTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/udj/0_6/players/1/users/user')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    newParticipant = Participant.objects.get(user__id=11, player__id=1)
