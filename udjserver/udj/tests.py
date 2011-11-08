"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket



class AuthTestCase(TestCase):
  fixtures = ['test_fixture.json']


  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test', 'password' : 'onetest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header('udj_ticket_hash'))
    self.assertTrue(response.has_header('user_id'))
    testUser = User.objects.filter(username='test')
    self.assertEqual(int(response.__getitem__('user_id')), testUser[0].id)
    ticket = Ticket.objects.filter(user=testUser)
    self.assertEqual(response.__getitem__('udj_ticket_hash'), ticket[0].ticket_hash)
