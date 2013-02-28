import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket


class AuthTests(TestCase):
  fixtures = ['test_fixture']
  client = Client()

  def issueTicketRequest(self, username='kurtis', password='testkurtis'):
    return self.client.post(
        '/udj/0_6/auth', {'username': username, 'password' : password})

  def getCurrentKurtisTicket(self):
    return Ticket.objects.get(user__username='kurtis')

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
    self.assertEqual(ticket_hash, self.getCurrentKurtisTicket().ticket_hash)

  def testDoubleAuth(self):
    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    self.assertEqual(user_id, self.getKurtisId())
    self.assertEqual(ticket_hash, self.getCurrentKurtisTicket().ticket_hash)

    response = self.issueTicketRequest()

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')

    ticket_and_user_id = json.loads(response.content)
    new_ticket = ticket_and_user_id['ticket_hash']

    self.assertEqual(new_ticket, ticket_hash)

  def testBadPassword(self):
    response = self.issueTicketRequest(password="badpassword")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')

  def testBadUsername(self):
    response = self.issueTicketRequest(username="wrongwrongwrong")

    self.assertEqual(response.status_code, 401, response.content)
    self.assertEqual(response['WWW-Authenticate'], 'password')
