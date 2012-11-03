from django.test import TestCase
from udj.external_library_resolvers import rdio


class RdioTests(TestCase):

  def testBasicSearch(self):
    results = rdio.search("deadmau5")
