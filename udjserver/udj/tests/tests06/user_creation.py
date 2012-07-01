import json

from udj.headers import CONFLICT_RESOURCE_HEADER

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class CreateUserTests(TestCase):
  fixtures = ['test_fixture']
  client = Client()

  def testBasicCreation(self):
    tocreate = {
        'username' : 'thesteve',
        'email' : 'steve@steve.com',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_6/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(201, response.status_code)
    newUser = User.objects.get(username=tocreate['username'])
    self.assertEqual(tocreate['email'], newUser.email)
    self.assertTrue(check_password(tocreate['password'], newUser.password))

