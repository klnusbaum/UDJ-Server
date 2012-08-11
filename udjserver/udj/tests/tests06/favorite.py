import json
from udj.models import LibraryEntry, Player, Favorite
from udj.testhelpers.tests06.testclasses import KurtisTestCase
from udj.headers import MISSING_RESOURCE_HEADER

class FavoritesTests(KurtisTestCase):

  def testAddFavorite(self):
    response = self.doPut('/udj/0_6/favorites/players/1/4')
    self.assertEqual(201, response.status_code)
    self.assertTrue(Favorite.objects.filter(
      user__id=2, favorite_song__player__id=1, favorite_song__player_lib_song_id=4).exists())

  def testAddFavoriteBadPlayer(self):
    response = self.doPut('/udj/0_6/favorites/players/90/4')
    self.assertEqual(404, response.status_code)
    self.assertEqual('player', response[MISSING_RESOURCE_HEADER])

  def testAddFavoriteBadSong(self):
    response = self.doPut('/udj/0_6/favorites/players/1/90')
    self.assertEqual(404, response.status_code)
    self.assertEqual('song', response[MISSING_RESOURCE_HEADER])

  def testRemoveFavoriteSong(self):
    response = self.doDelete('/udj/0_6/favorites/players/1/7')
    self.assertEqual(200, response.status_code)
    self.assertFalse(Favorite.objects.filter(
      user__id=2, favorite_song__player__id=1, favorite_song__player_lib_song_id=7).exists())

  def testBadFavoriteRemove(self):
    response = self.doDelete('/udj/0_6/favorites/players/1/11')
    self.assertEqual(404, response.status_code)
    self.assertEqual('song', response[MISSING_RESOURCE_HEADER])

  def testGetFavorites(self):
    response = self.doGet('/udj/0_6/favorites/players/1')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    favorites = json.loads(response.content)
    self.assertTrue(2, len(favorites))
    libids = [fav["id"] for fav in favorites]
    self.assertTrue('7' in libids)
    self.assertTrue('8' in libids)


