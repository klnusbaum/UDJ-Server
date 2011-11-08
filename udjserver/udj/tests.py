"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client



class AuthTestCase(TestCase):
  fixtures = ['test_fixture.json']


  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth/', {'username': 'test', 'password' : 'onetest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header('udj_ticket_hash'))
    self.assertTrue(response.has_header('user_id'))
    
class LibAddTest(TestCase):
  fixtrues = ['test_fixture.json']

  def testAdd(self):
    client = Client()
    response = client.get('/udj/')
    self.assertEqual(response.status_code, 200)
    
