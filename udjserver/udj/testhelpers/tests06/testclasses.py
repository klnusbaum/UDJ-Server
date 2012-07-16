import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.models import Player, PlayerPassword, PlayerLocation
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

class PasswordModificationTests(DoesServerOpsTestCase):

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

