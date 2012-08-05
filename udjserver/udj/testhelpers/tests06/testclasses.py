import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket, Participant
from udj.headers import DJANGO_TICKET_HEADER, MISSING_RESOURCE_HEADER
from udj.models import Player, PlayerPassword, PlayerLocation, PlayerAdmin
from udj.views.views06.auth import hashPlayerPassword

from datetime import datetime
from datetime import timedelta

class DoesServerOpsTestCase(TestCase):
  fixtures = ['test_fixture']
  client = Client()

  def setUp(self):
    response = self.client.post(
      '/udj/0_6/auth', {'username': self.username, 'password' : self.userpass})
    self.assertEqual(response.status_code, 200)
    ticket_and_user_id = json.loads(response.content)
    self.ticket_hash = ticket_and_user_id['ticket_hash']
    self.user_id = ticket_and_user_id['user_id']

  def doJSONPut(self, url, payload, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(
      url,
      data=payload, content_type='text/json',
      **headers)

  def doPut(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(url, **headers)

  def doGet(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.get(url, **headers)

  def doDelete(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.delete(url, **headers)

  def doPost(self, url, args={}, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.post(url, args, **headers)

  def isJSONResponse(self, response):
    self.assertEqual(response['Content-Type'], 'text/json')


class KurtisTestCase(DoesServerOpsTestCase):
  username = "kurtis"
  userpass = "testkurtis"

class JeffTestCase(DoesServerOpsTestCase):
  username = "jeff"
  userpass = "testjeff"

class YunYoungTestCase(DoesServerOpsTestCase):
  username = "yunyoung"
  userpass = "testyunyoung"

class AlejandroTestCase(DoesServerOpsTestCase):
  username = "alejandro"
  userpass = "testalejandro"

class LucasTestCase(DoesServerOpsTestCase):
  username = "lucas"
  userpass = "testlucas"

class LeeTestCase(DoesServerOpsTestCase):
  username = "lee"
  userpass = "testlee"

class ZachTestCase(DoesServerOpsTestCase):
  username = "zach"
  userpass = "testzach"

class BasicPlayerAdministrationTests(DoesServerOpsTestCase):

  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/udj/0_6/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }

    response = self.doPost('/udj/0_6/players/1/location', newLocation)
    self.assertEqual(response.status_code, 200)
    playerLocation = PlayerLocation.objects.get(player__id=1)
    self.assertEqual(newLocation['address'], playerLocation.address)
    self.assertEqual(newLocation['locality'], playerLocation.locality)
    self.assertEqual(newLocation['region'], playerLocation.region)
    self.assertEqual(newLocation['postal_code'], playerLocation.postal_code)
    self.assertEqual(newLocation['country'], playerLocation.country)
    self.assertEqual(-93.481394, playerLocation.point.x)
    self.assertEqual(44.981806, playerLocation.point.y)

  def testSetLocationWithNoPreviousLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }


    response = self.doPost('/udj/0_6/players/4/location', newLocation)
    self.assertEqual(200, response.status_code)
    playerLocation = PlayerLocation.objects.get(player__id=4)
    self.assertEqual(newLocation['address'], playerLocation.address)
    self.assertEqual(newLocation['locality'], playerLocation.locality)
    self.assertEqual(newLocation['region'], playerLocation.region)
    self.assertEqual(newLocation['postal_code'], playerLocation.postal_code)
    self.assertEqual(newLocation['country'], playerLocation.country)
    self.assertEqual(-93.481394, playerLocation.point.x)
    self.assertEqual(44.981806, playerLocation.point.y)

  def testAddAdmin(self):
    response = self.doPut('/udj/0_6/players/1/admins/7')
    self.assertEqual(201, response.status_code)
    self.assertTrue(PlayerAdmin.objects.filter(admin_user__id=7, player__id=1).exists())

  def testNonExistentAdminAdd(self):
    response = self.doPut('/udj/0_6/players/1/admins/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])


  def testRemoveAdmin(self):
    response = self.doDelete('/udj/0_6/players/1/admins/1')
    self.assertEqual(200, response.status_code)
    self.assertFalse(PlayerAdmin.objects.filter(admin_user__id=1, player__id=1).exists())

  def testNonExistsentAdminRemove(self):
    response = self.doDelete('/udj/0_6/players/1/admins/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testKickUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/3')
    self.assertEqual(200, response.status_code)
    kickedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, kickedUser.kick_flag)

  def testKickNonParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testKickNonExistentUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testBanParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/3')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/1')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=1, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonExistentUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/10000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/8')
    self.assertEqual(200, response.status_code)
    bannedUser = Participant.objects.get(user__id=8, player__id=1)
    self.assertEqual(False, bannedUser.ban_flag)

  def testUnbanNonParticipatingUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanNonExistentUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/1000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])


  def testGetBannedUsers(self):
    response = self.doGet('/udj/0_6/players/1/banned_users')
    self.assertEqual(200, response.status_code)
    bannedUsers = json.loads(response.content)
    self.assertEqual(1, len(bannedUsers))
    self.assertEqual(8, bannedUsers[0]['id'])




class PasswordAdministrationTests(DoesServerOpsTestCase):

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

