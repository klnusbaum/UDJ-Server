import json
from udj.models import Participant
from datetime import datetime
from udj.testhelpers.tests06.testclasses import ZachTestCase
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER, FORBIDDEN_REASON_HEADER
from udj.testhelpers.tests06.decorators import EnsureParticipationUpdated

class BeginParticipateTests(ZachTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/udj/0_6/players/5/users/user')
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=5)

  def testPasswordPlayer(self):
    response = self.doPut('/udj/0_6/players/3/users/user',
        {DJANGO_PLAYER_PASSWORD_HEADER : 'alejandro'})
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=3)

  def testBadPassword(self):
    response = self.doPut('/udj/0_6/players/3/users/user',
        {DJANGO_PLAYER_PASSWORD_HEADER : 'wrong'})
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')

  def testBannedFromPlayer(self):
    response = self.doPut('/udj/0_6/players/1/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'banned')

  def testFullPlayer(self):
    response = self.doPut('/udj/0_6/players/7/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'player-full')

  @EnsureParticipationUpdated(8, 6)
  def testClearKickFlag(self):
    zach = Participant.objects.get(user__id=8, player__id=6)
    self.assertEqual(zach.kick_flag, True)
    response = self.doPut('/udj/0_6/players/6/users/user')
    self.assertEqual(response.status_code, 201)
    zach = Participant.objects.get(player__id=6, user__id=8)
    self.assertEqual(zach.kick_flag, False)

