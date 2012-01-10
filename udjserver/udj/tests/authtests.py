from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.headers import getTicketHeader
from udj.headers import getUserIdHeader
from udj.models import Ticket
class AuthTest(TestCase):
  fixtures = ['test_fixture.json']

  def testAuth(self):
    client = Client()
    response = client.post('/udj/auth', {'username': 'test2', 'password' : 'twotest'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.has_header(getTicketHeader()))
    self.assertTrue(response.has_header(getUserIdHeader()))
    testUser = User.objects.filter(username='test2')
    self.assertEqual(
      int(response.__getitem__(getUserIdHeader())), testUser[0].id)
    ticket = Ticket.objects.filter(user=testUser)
    self.assertEqual(response.__getitem__(getTicketHeader()), ticket[0].ticket_hash)


