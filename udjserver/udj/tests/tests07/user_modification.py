import json

from udj.headers import CONFLICT_RESOURCE_HEADER, NOT_ACCEPTABLE_REASON_HEADER
from udj.testhelpers.tests07.testclasses import YunYoungTestCase

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

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(201, response.status_code)
    newUser = User.objects.get(username=tocreate['username'])
    self.assertEqual(tocreate['email'], newUser.email)
    self.assertTrue(check_password(tocreate['password'], newUser.password))
    self.assertEqual(newUser.first_name, "")
    self.assertEqual(newUser.last_name, "")

  def testNameCreation(self):
    tocreate = {
        'username' : 'thesteve',
        'email' : 'steve@steve.com',
        'password' : 'bigcheese',
        'first_name' : 'steve',
        'last_name' : 'steveson'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(201, response.status_code)
    newUser = User.objects.get(username=tocreate['username'])
    self.assertEqual(tocreate['email'], newUser.email)
    self.assertTrue(check_password(tocreate['password'], newUser.password))
    self.assertEqual(tocreate['first_name'], newUser.first_name)
    self.assertEqual(tocreate['last_name'], newUser.last_name)


  def testDuplicateEmail(self):
    tocreate = {
        'username' : 'thesteve',
        'email' : 'kurtis@kurtis.com',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(409, response.status_code)
    self.assertEqual('email', response[CONFLICT_RESOURCE_HEADER])

  def testDuplicateUsername(self):
    tocreate = {
        'username' : 'kurtis',
        'email' : 'kurtis@thebomb.net',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(409, response.status_code)
    self.assertEqual('username', response[CONFLICT_RESOURCE_HEADER])

  def testBadJson(self):
    tocreate = {
        'username' : 'steve',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(400, response.status_code)

  def testShortPassword(self):
    tocreate = {
        'username' : 'thesteve',
        'email' : 'steve@steve.com',
        'password' : 'short'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(406, response.status_code)
    self.assertEqual('password', response[NOT_ACCEPTABLE_REASON_HEADER])

  def testBadUsername(self):
    tocreate = {
        'username' : ' ',
        'email' : 'steve@steve.com',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(406, response.status_code)
    self.assertEqual('username', response[NOT_ACCEPTABLE_REASON_HEADER])

  def testBadEmail(self):
    tocreate = {
        'username' : 'thesteve',
        'email' : 'steve',
        'password' : 'bigcheese'
    }

    response = self.client.put('/udj/0_7/user', data=json.dumps(tocreate), content_type="text/json")
    self.assertEqual(406, response.status_code)
    self.assertEqual('email', response[NOT_ACCEPTABLE_REASON_HEADER])


class ModifyUserTests(YunYoungTestCase):
  def testChangeName(self):
    payload = {
        'username' : 'yunyoung',
        'password' : 'testyunyoung',
        'email' : 'yunyoung@yy.com',
        'first_name' : 'youyoung',
        'last_name' : 'differnt'
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(200, response.status_code)

    user = User.objects.get(username='yunyoung')
    self.assertEqual(user.first_name, payload['first_name'])
    self.assertEqual(user.last_name, payload['last_name'])

  def testEmailChange(self):
    payload = {
        'username' : 'yunyoung',
        'password' : 'testyunyoung',
        'email' : 'yunyoung1@yy.com',
        'first_name' : '',
        'last_name' : ''
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(200, response.status_code)

    user = User.objects.get(username='yunyoung')
    self.assertEqual(user.email, payload['email'])


  def testBadUsernameChange(self):
    payload = {
        'username' : 'yunyoung1',
        'password' : 'testyunyoung',
        'email' : 'yunyoung@yy.com',
        'first_name' : 'steve',
        'last_name' : ''
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(406, response.status_code)
    self.assertEqual('username', response[NOT_ACCEPTABLE_REASON_HEADER])


    user = User.objects.get(username='yunyoung')
    self.assertEqual('', user.first_name)

  def testBadEmailChange(self):
    payload = {
        'username' : 'yunyoung',
        'password' : 'testyunyoung',
        'email' : 'yunyoung',
        'first_name' : 'steve',
        'last_name' : ''
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(406, response.status_code)
    self.assertEqual('email', response[NOT_ACCEPTABLE_REASON_HEADER])


    user = User.objects.get(username='yunyoung')
    self.assertEqual('', user.first_name)
    self.assertEqual('yunyoung@yy.com', user.email)

  def testDuplicateEmailChange(self):
    payload = {
        'username' : 'yunyoung',
        'password' : 'testyunyoung',
        'email' : 'lucas@lucas.com',
        'first_name' : 'steve',
        'last_name' : ''
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(409, response.status_code)
    self.assertEqual('email', response[CONFLICT_RESOURCE_HEADER])


    user = User.objects.get(username='yunyoung')
    self.assertEqual('', user.first_name)
    self.assertEqual('yunyoung@yy.com', user.email)


  def testBadPasswordChange(self):
    payload = {
        'username' : 'yunyoung',
        'password' : 'short',
        'email' : 'yunyoung@yy.com',
        'first_name' : 'steve',
        'last_name' : ''
      }
    response = self.doJSONPost('/user', payload)
    self.assertEqual(406, response.status_code)
    self.assertEqual('password', response[NOT_ACCEPTABLE_REASON_HEADER])


    user = User.objects.get(username='yunyoung')
    self.assertEqual('', user.first_name)
    self.assertTrue(check_password('testyunyoung', user.password))




