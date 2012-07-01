import json
from udj.models import LibraryEntry, Player, Favorite
from udj.tests.tests06.testhelpers import KurtisTestCase

class FavoritesTests(KurtisTestCase):

  def testAddFavorite(self):
    response = self.doPut('/udj/0_6/favorites/players/1/4')
    self.assertEqual(201, response.status_code)
    self.assertTrue(Favorite.objects.filter(
      user__id=2, favorite_song__player__id=1, favorite_song__player_lib_song_id=4).exists)
