import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
from udj.headers import DJANGO_TICKET_HEADER

class DoesServerOpsTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()

  def setUp(self):
    headers = {}
    response = self.client.post(
      '/udj/auth', {'username': self.username, 'password' : self.userpass},
      **headers)
    self.assertEqual(response.status_code, 200)
    ticket_and_user_id = json.loads(response.content)
    self.ticket_hash = ticket_and_user_id['ticket_hash']
    self.user_id = ticket_and_user_id['user_id']

  def doJSONPut(self, url, payload, headers={}):
    headers[getDjangoTicketHeader()] = self.ticket_hash
    return self.client.put(
      url,
      data=payload, content_type='text/json',
      **headers)

  def doPut(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(url, **headers)

  def doGet(self, url):
    return self.client.get(url, **{DJANGO_TICKET_HEADER : self.ticket_hash})

  def doDelete(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.delete(url, **headers)

  def doPost(self, url, args):
    return self.client.post(url, args, **{DJANGO_TICKET_HEADER : self.ticket_hash})

  def isJSONResponse(self, response):
    self.assertEqual(response['Content-Type'], 'text/json')

class KurtisTestCase(DoesServerOpsTestCase):
  username = "kurtis"
  userpass = "testkurtis"

