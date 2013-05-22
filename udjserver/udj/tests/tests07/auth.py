import json
from datetime import timedelta, datetime

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from udj.models import Ticket, FbUser
from udj.headers import DJANGO_TICKET_HEADER
from udj.testhelpers.tests07.testclasses import BasicUDJTestCase

from settings import TICKET_VALIDITY_LENGTH, FB_TEST_ACCESS_TOKEN, FB_TEST_USER_ID


class AuthTests(BasicUDJTestCase):

  def issueTicketRequest(self, username='kurtis', password='testkurtis'):
    return self.client.post(
        '/udj/0_7/auth', json.dumps({'username': username, 'password' : password}),
        content_type="text/json")

  def getKurtisId(self):
    return str(User.objects.get(username='kurtis').id)

  def testAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, self.getKurtisId())
    self.assertTrue(Ticket.objects.filter(user=User.objects.get(username='kurtis')).exists())

  def testDoubleAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, self.getKurtisId())
    self.assertTrue(Ticket.objects.filter(user__id=user_id, ticket_hash=ticket_hash).exists())

    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    new_ticket = ticket_and_user_id['ticket_hash']

    self.assertNotEqual(new_ticket, ticket_hash)


  def testBadPassword(self):
    response = self.issueTicketRequest(password="badpassword")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')


  def testBadUsername(self):
    response = self.issueTicketRequest(username="wrongwrongwrong")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')

  def testExpiredTicket(self):
    INVALID_LENGTH = TICKET_VALIDITY_LENGTH + timedelta(days=1)
    ticket = Ticket.objects.get(pk=1)
    ticket.time_last_used = datetime.now() - INVALID_LENGTH
    ticket.time_issued = datetime.now() - INVALID_LENGTH
    ticket.save()

    response = self.client.get('/udj/0_7/sorting_algorithms', 
                               {DJANGO_TICKET_HEADER : ticket.ticket_hash})

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'ticket-hash')


class FbAuthTests(BasicUDJTestCase):

  def testFbAuth(self):
    import requests
    params = {
              "user_id" : FB_TEST_USER_ID,
              "access_token" : FB_TEST_ACCESS_TOKEN
            }
    response = self.client.post('/udj/0_7/fb_auth', json.dumps(params), content_type='text/json')

    self.assertEqual(response.status_code, 200, response.content)
    fb_user = FbUser.objects.get(fb_user_id=FB_TEST_USER_ID)
    actual_user = fb_user.user

    params = {
        "fields" : "last_name,first_name,email,username",
        "access_token" : FB_TEST_ACCESS_TOKEN
        }
    url = "https://graph.facebook.com/{0}".format(FB_TEST_USER_ID)
    user_request = requests.get(url, params=params)
    user_data = json.loads(user_request.text)
    self.assertEqual(user_data['email'], actual_user.email)
    self.assertEqual(user_data['first_name'], actual_user.first_name)
    self.assertEqual(user_data['last_name'], actual_user.last_name)
    self.assertEqual(user_data['username'], actual_user.username)


  def testBadFbAuth(self):
    params = {
              "user_id" : "1278780539",
              "access_token" : "badtoken"
             }
    response = self.client.post('/udj/0_7/fb_auth', json.dumps(params), content_type='text/json')

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'access-token')

