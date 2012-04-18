import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER

class DoesServerOpsTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  port = 4034
  address = "55.33.44.22"
  machine_headers = {"REMOTE_PORT" : port , "REMOTE_ADDR" : address}

  def setUp(self):
    response = self.client.post(
      '/udj/auth', {'username': self.username, 'password' : self.userpass},
      **DoesServerOpsTestCase.machine_headers)
    self.assertEqual(response.status_code, 200)
    ticket_and_user_id = json.loads(response.content)
    self.ticket_hash = ticket_and_user_id['ticket_hash']
    self.user_id = ticket_and_user_id['user_id']

  def doJSONPut(self, url, payload, headers={}):
    headers = dict(headers.items() + DoesServerOpsTestCase.machine_headers.items())
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(
      url,
      data=payload, content_type='text/json',
      **headers)

  def doPut(self, url, headers={}):
    headers = dict(headers.items() + DoesServerOpsTestCase.machine_headers.items())
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(url, **headers)

  def doGet(self, url):
    headers = DoesServerOpsTestCase.machine_headers
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.get(url, **headers)

  def doDelete(self, url, headers={}):
    headers = dict(headers.items() + DoesServerOpsTestCase.machine_headers.items())
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.delete(url, **headers)

  def doPost(self, url, args):
    headers = dict(DoesServerOpsTestCase.machine_headers.items())
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
