import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER
from udj.models import Participant

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

def EnsureParticipationUpdated(user_id, player_id):
  def decorator(target):
    def wrapper(*args, **kwargs):
      participant = Participant.objects.get(user__id=user_id, player__id=player_id)
      oldTime = participant.time_last_interaction
      participant.save()
      target(*args, **kwargs)
      newTime = Participant.objects.get(user__id=user_id, player__id=player_id).time_last_interaction
      (args[0]).assertTrue(newTime > oldTime)
    return wrapper
  return decorator

