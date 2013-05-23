import json
import udj
from udj.models import Participant, SongSet, SongSetEntry, LibraryEntry, Player, PlayerPermissionGroup, PlayerPermission, Library
from datetime import datetime
from udj.testhelpers.tests07.testclasses import ZachTestCase, LeeTestCase, MattTestCase
"""
, MattTestCase, JeffTestCase, LeeTestCase, KurtisTestCase
"""
from udj.headers import FORBIDDEN_REASON_HEADER
from udj.testhelpers.tests07.decorators import EnsureParticipationUpdated

import udj.resolvers.standard

class BeginParticipateTests(ZachTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/players/5/users/user')
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=5)

  def testPasswordPlayerMethod(self):
    response = self.doJSONPut('/players/3/users/user', {'password' : 'alejandro'})
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=3)

  def testBadPassword(self):
    response = self.doJSONPut('/players/3/users/user', {'password' : 'wrong'})
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')

  def testBannedFromPlayer(self):
    response = self.doPut('/players/1/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'banned')

  def testFullPlayer(self):
    response = self.doPut('/players/7/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'player-full')

  def testNoPermissionPlayer(self):
    tempgroup = PlayerPermissionGroup.objects.get(pk=4)
    tempplayer = Player.objects.get(pk=4)
    PlayerPermission(player=tempplayer, group=tempgroup, permission=u'PWP').save()
    response = self.doPut('/players/4/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'player-permission')

  @EnsureParticipationUpdated(8, 6)
  def testClearKickFlag(self):
    zach = Participant.objects.get(user__id=8, player__id=6)
    self.assertEqual(zach.kick_flag, True)
    response = self.doPut('/players/6/users/user')
    self.assertEqual(response.status_code, 201)
    zach = Participant.objects.get(player__id=6, user__id=8)
    self.assertEqual(zach.kick_flag, False)

class LoginAfterLogout(LeeTestCase):
  def testLogin(self):
    response = self.doPut('/players/1/users/user')
    self.assertEqual(response.status_code, 201)
    lee = Participant.objects.get(user__id=11, player__id=1)
    self.assertEqual(False, lee.logout_flag)

class GetUsersTests(MattTestCase):
  def setUp(self):
    super(GetUsersTests, self).setUp()
    matt = Participant.objects.get(user__id=9, player__id=7)
    matt.time_last_interaction = datetime.now()
    matt.save()

  @EnsureParticipationUpdated(9, 7)
  def testGetUsersSingle(self):
    response = self.doGet('/players/7/users')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    users = json.loads(response.content)
    self.assertEqual(1, len(users))
    expectedIds = ['9']
    for user in users:
      self.assertTrue(user['id'] in expectedIds)

  @EnsureParticipationUpdated(9, 7)
  def testGetUsersBoth(self):
    alex = Participant.objects.get(user__id=10, player__id=7)
    alex.time_last_interaction = datetime.now()
    alex.save()
    response = self.doGet('/players/7/users')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    users = json.loads(response.content)
    self.assertEqual(2, len(users))
    expectedIds = ['9', '10']
    for user in users:
      self.assertTrue(user['id'] in expectedIds)



class GetAvailableMusicTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3,1)
  def testGetBasicMusic(self):
    response = self.doGet('/players/1/available_music?query=Third+Eye+Blind')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(4, len(songResults))
    expectedLibIds =['1','2','3','5']
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(3, 1)
  def testSimpleGetWithMax(self):
    response = self.doGet('/players/1/available_music?query=Third+Eye+Blind&max_results=2')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))

  @EnsureParticipationUpdated(3, 1)
  def testAlbumGet(self):
    response = self.doGet('/players/1/available_music?query=Bedlam+in+Goliath')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    expectedLibIds =['6','7']
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

class GetAvailableMusicTestsRdio(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid = 8


  @EnsureParticipationUpdated(3,8)
  def testGetBasicMusic(self):
    response = self.doGet('/players/8/available_music?query=Third+Eye+Blind')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertTrue(len(songResults) > 4)

  @EnsureParticipationUpdated(3,8)
  def testSimpleGetWithMax(self):
    response = self.doGet('/players/8/available_music?query=Third+Eye+Blind&max_results=2')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))


class GetArtistsTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid = 1

  @EnsureParticipationUpdated(3,1)
  def testGetArtists(self):
    response = self.doGet('/players/1/available_music/artists')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(3, len(jsonResponse))
    requiredArtists = [u'Skrillex', u'The Mars Volta', u'Third Eye Blind']
    for artist in jsonResponse:
      self.assertTrue(artist in requiredArtists)

  def testGetArtistSongsStandardResolver(self):
    songs = udj.resolvers.standard.getSongsForArtist("Third Eye Blind",
                                                     Library.objects.get(pk=1),
                                                     Player.objects.get(pk=1)
                                                    )
    self.assertEqual(4, len(songs))
    requiredIds = ['1', '2', '3', '5']
    for songId in [x.lib_id for x in songs]:
      self.assertTrue(songId in requiredIds)

  @EnsureParticipationUpdated(3,1)
  def testSpecificArtistGet(self):
    response = self.doGet('/players/1/available_music/artists/Third Eye Blind')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(4, len(jsonResponse))
    requiredIds = ['1', '2', '3', '5']
    for songId in [x['id'] for x in jsonResponse]:
      self.assertTrue(songId in requiredIds)

class GetRdioArtistsTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid = 8

  @EnsureParticipationUpdated(3,8)
  def testGetArtists(self):
    response = self.doGet('/players/8/available_music/artists')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    #This is bad, we should really only be getting back 3 but I don't
    #really have a good way of merging results from different libraries yet :/
    self.assertEqual(4, len(jsonResponse))
    requiredArtists = [u'Skrillex', u'The Mars Volta', u'Third Eye Blind']
    for artist in jsonResponse:
      self.assertTrue(artist in requiredArtists)

  @EnsureParticipationUpdated(3,8)
  def testSpecificArtistGet(self):
    response = self.doGet('/players/8/available_music/artists/Skrillex')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)

    standard_songs = udj.resolvers.standard.getSongsForArtist("Skrillex",
                                                              Library.objects.get(pk=1),
                                                              Player.objects.get(pk=8))
    rdio_songs = udj.resolvers.rdio.getSongsForArtist("Skrillex",
                                                      Library.objects.get(pk=8),
                                                      Player.objects.get(pk=8))

    #This next part is two fold. not only does it ensure we get the correct
    #overall response, but it ensures that everything we get back
    #was also added to the database like it was supposed to be
    #the only thing is that it doesn't verify that we get everything we're
    #supposed to get from Rdio. I can't think of a good way to do that :/
    db_ids = [x.lib_id for x in standard_songs]
    db_ids.extend([x.lib_id for x in rdio_songs])
    self.assertTrue(0 < len(db_ids))
    self.assertEqual(len(db_ids), len(jsonResponse))
    for songId in [x['id'] for x in jsonResponse]:
      self.assertTrue(songId in db_ids, "Not found Song: " + str(songId))


class GetRecentlyPlayed(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3,1)
  def testRecentlyPlayed(self):
    response = self.doGet('/players/1/recently_played')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(2, len(jsonResponse))
    self.assertEqual('7', jsonResponse[0]['song']['id'])
    self.assertEqual('5', jsonResponse[1]['song']['id'])

  @EnsureParticipationUpdated(3,1)
  def testRecentlyPlayedWithDeletion(self):
    to_delete = LibraryEntry.objects.get(pk=5)
    to_delete.is_deleted = True
    to_delete.save()
    response = self.doGet('/players/1/recently_played')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(1, len(jsonResponse))
    self.assertEqual('7', jsonResponse[0]['song']['id'])


  @EnsureParticipationUpdated(3, 1)
  def testRecentlyPlayedWithMax(self):
    response = self.doGet('/players/1/recently_played?max_songs=1')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(1, len(jsonResponse))

class GetRandoms(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3,1)
  def testSimpleGetRandom(self):
    response = self.doGet('/players/1/available_music/random_songs?max_randoms=2')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    for song in songResults:
      self.assertFalse(LibraryEntry.objects.get(library__id=int(song['library_id']),
                                                lib_id=song['id']).is_deleted)
      self.assertFalse(LibraryEntry.objects.get(library__id=int(song['library_id']),
                                                lib_id=song['id'])
                                                .is_banned(Player.objects.get(pk=1)))

class GetRdioRandoms(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=8

  @EnsureParticipationUpdated(3,8)
  def testSimpleGetRandom(self):
    response = self.doGet('/players/8/available_music/random_songs?max_randoms=4')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(4, len(songResults))
    for song in songResults:
      self.assertFalse(LibraryEntry.objects.get(library__id=int(song['library_id']),
                                                lib_id=song['id']).is_deleted)
      self.assertFalse(LibraryEntry.objects.get(library__id=int(song['library_id']),
                                                lib_id=song['id'])
                                                .is_banned(Player.objects.get(pk=8)))

"""
class LogoutTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  def testLogout(self):
    response = self.doDelete('/players/1/users/user')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(True, Participant.objects.get(user__id=3, player__id=1).logout_flag)
    activeUserIds = [x.user.id for x in Player.objects.get(id=1).ActiveParticipants]
    self.assertFalse(3 in activeUserIds)


class OwnerCurrentSongTestCase(udj.testhelpers.tests07.testclasses.CurrentSongTestCase):
  username="kurtis"
  userpass="testkurtis"


class AdminCurrentSongTestCase(udj.testhelpers.tests07.testclasses.CurrentSongTestCase):
  username="lucas"
  userpass="testlucas"

  def setUp(self):
    super(udj.testhelpers.tests07.testclasses.CurrentSongTestCase, self).setUp()
    lucas = Participant.objects.get(user__id=5, player__id=1)
    lucas.time_last_interaction = datetime.now()
    lucas.save()
    self.oldtime = lucas.time_last_interaction


  def tearDown(self):
    lucas = Participant.objects.get(user__id=5, player__id=1)
    self.assertTrue(lucas.time_last_interaction > self.oldtime)

class OwnerBlankCurrentSongTestCase(udj.testhelpers.tests07.testclasses.BlankCurrentSongTestCase):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminBlankCurrentSongTestCase(udj.testhelpers.tests07.testclasses.BlankCurrentSongTestCase):
  username="kurtis"
  userpass="testkurtis"

  def setUp(self):
    super(udj.testhelpers.tests07.testclasses.BlankCurrentSongTestCase, self).setUp()
    kurtis = Participant.objects.get(user__id=2, player__id=3)
    kurtis.time_last_interaction = datetime.now()
    kurtis.save()
    self.oldtime = kurtis.time_last_interaction

  def tearDown(self):
    kurtis = Participant.objects.get(user__id=2, player__id=3)
    self.assertTrue(kurtis.time_last_interaction > self.oldtime)
"""
