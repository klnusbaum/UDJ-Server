"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.headers import getTicketHeader
from udj.headers import getDjangoTicketHeader
from udj.headers import getUserIdHeader
from udj.models import Ticket

class DoesServerOpsTestCase(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  
  def setUp(self):
    response = self.client.post(
      '/udj/auth', {'username': self.username, 'password' : self.userpass})
    self.assertEqual(response.status_code, 200)
    self.ticket_hash = response.__getitem__(getTicketHeader())
    self.user_id = response.__getitem__(getUserIdHeader())

  def doJSONPut(self, url, payload):
   return self.client.put(
      url,
      data=payload, content_type='text/json', 
      **{getDjangoTicketHeader() : self.ticket_hash})

  def doPut(self, url):
   return self.client.put(url, **{getDjangoTicketHeader() : self.ticket_hash})

  def doGet(self, url):
    return self.client.get(url, **{getDjangoTicketHeader() : self.ticket_hash})
   
  def doDelete(self, url):
    return self.client.delete(url, **{getDjangoTicketHeader() : self.ticket_hash})

  def doPost(self, url, args):
    return self.client.post(url, args, **{getDjangoTicketHeader() : self.ticket_hash})
  
  def verifyJSONResponse(self, response):
    self.assertEqual(response['Content-Type'], 'text/json')

class User2TestCase(DoesServerOpsTestCase):
  username = "test2"
  userpass = "twotest"

class User3TestCase(DoesServerOpsTestCase):
  username = "test3"
  userpass = "threetest"

class User4TestCase(DoesServerOpsTestCase):
  username = "test4"
  userpass = "fourtest"

class User5TestCase(DoesServerOpsTestCase):
  username = "test5"
  userpass = "fivetest"

class User8TestCase(DoesServerOpsTestCase):
  username = "test8"
  userpass = "eighttest"

