import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket
class AuthTest(TestCase):
  fixtures = ['test_fixture.json']

  def testAuth(self):
    client = Client()
    port = 4034
    address = "55.33.44.22"
    headers = {"REMOTE_PORT" : port , "REMOTE_ADDR" : address}
    response = client.post('/udj/auth', {'username': 'kurtis', 'password' : 'testkurtis'}, **headers)

    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(response['Content-Type'], 'text/json')


    ticket_and_user_id = json.loads(response.content)
    ticket_hash = ticket_and_user_id['ticket_hash']
    user_id = ticket_and_user_id['user_id']

    kurtis = User.objects.get(username='kurtis')
    self.assertEqual(user_id, kurtis.id)
    ticket = Ticket.objects.get(user=kurtis, source_ip_addr=address, source_port=port)
    self.assertEqual(ticket_hash, ticket.ticket_hash)

  """
  def testDoubleTicket(self):
    client = Client()
    headers = {}
    headers[getDjangoApiVersionHeader()] = "0.2"
    response = client.post(
      '/udj/auth', {'username': 'test2', 'password' : 'twotest'}, **headers)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header(getTicketHeader()))
    self.assertTrue(response.has_header(getUserIdHeader()))
    testUser = User.objects.filter(username='test2')
    self.assertEqual(
      int(response.__getitem__(getUserIdHeader())), testUser[0].id)
    ticket = Ticket.objects.get(user=testUser)
    firstTicket = response[getTicketHeader()]
    firstTime = ticket.time_issued
    self.assertEqual(firstTicket, ticket.ticket_hash)
    response = client.post(
      '/udj/auth', {'username': 'test2', 'password' : 'twotest'}, **headers)
    ticket = Ticket.objects.get(user=testUser)
    secondTicket = response[getTicketHeader()]
    secondTime = ticket.time_issued
    self.assertNotEqual(firstTicket, secondTicket)
    self.assertEqual(secondTicket, ticket.ticket_hash)
    self.assertTrue(secondTime > firstTime)
    """
