import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket


class AuthTest(TestCase):
  fixtures = ['test_fixture.json']
  client = Client()
  port = 4034
  address = "55.33.44.22"
  headers = {"REMOTE_PORT" : port , "REMOTE_ADDR" : address}
  kurtis = User.objects.get(username='kurtis')

  def issueTicketRequest(self):
    return self.client.post(
        '/udj/auth', {'username': 'kurtis', 'password' : 'testkurtis'}, **AuthTest.headers)

  @staticmethod
  def getCurrentTicket():
    return Ticket.objects.get(
      user=AuthTest.kurtis, source_ip_addr=AuthTest.address, source_port=AuthTest.port)

  def testAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, AuthTest.kurtis.id)
    self.assertEqual(ticket_hash, AuthTest.getCurrentTicket().ticket_hash)

  def testDoubleTicket(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json')

    ticket_and_user_id = json.loads(response.content)
    first_ticket = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(first_ticket, AuthTest.getCurrentTicket().ticket_hash)
    firstTime = AuthTest.getCurrentTicket().time_issued

    response = self.issueTicketRequest()

    ticket_and_user_id = json.loads(response.content)
    second_ticket = ticket_and_user_id['ticket_hash']

    secondTime = AuthTest.getCurrentTicket().time_issued

    self.assertNotEqual(first_ticket, second_ticket)
    self.assertEqual(second_ticket, AuthTest.getCurrentTicket().ticket_hash)
    self.assertTrue(secondTime > firstTime)
