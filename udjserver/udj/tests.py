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
#    response = client.post('/udj/auth/')
    self.assertEqual(response.status_code, 200)
    
class SanityTestCase(TestCase):
  fixtrues = ['test_fixture.json']

  def testSanity(self):
    client = Client()
    response = client.get('/udj/')
    self.assertEqual(response.status_code, 200)
    
