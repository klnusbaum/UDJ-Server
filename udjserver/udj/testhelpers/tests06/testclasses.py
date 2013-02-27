import json
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from udj.models import Ticket, Participant, ActivePlaylistEntry, LibraryEntry
from udj.headers import DJANGO_TICKET_HEADER, MISSING_RESOURCE_HEADER
from udj.models import Player, PlayerPassword, PlayerLocation, PlayerAdmin, ActivePlaylistEntry, PlaylistEntryTimePlayed
from udj.views.views06.auth import hashPlayerPassword

from datetime import datetime
from datetime import timedelta

class DoesServerOpsTestCase(TestCase):
  fixtures = ['test_fixture']
  client = Client()

  def setUp(self):
    response = self.client.post(
      '/udj/0_6/auth', {'username': self.username, 'password' : self.userpass})
    self.assertEqual(response.status_code, 200)
    ticket_and_user_id = json.loads(response.content)
    self.ticket_hash = ticket_and_user_id['ticket_hash']
    self.user_id = ticket_and_user_id['user_id']

  def doJSONPut(self, url, payload, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(
      url,
      data=payload, content_type='text/json',
      **headers)

  def doPut(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.put(url, **headers)

  def doGet(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.get(url, **headers)

  def doDelete(self, url, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.delete(url, **headers)

  def doPost(self, url, args={}, headers={}):
    headers[DJANGO_TICKET_HEADER] = self.ticket_hash
    return self.client.post(url, args, **headers)

  def isJSONResponse(self, response):
    self.assertEqual(response['Content-Type'], 'text/json; charset=utf-8')


class BasicPlayerAdministrationTests(DoesServerOpsTestCase):

  def testSetVolume(self):
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)
    response = self.doPost('/udj/0_6/players/1/volume', {'volume' : 2})
    self.assertEqual(response.status_code, 200)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 2)

  def testBadVolumeSet(self):
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)
    response = self.doPost('/udj/0_6/players/1/volume', {'volume' : 11})
    self.assertEqual(response.status_code, 400)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)


  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/udj/0_6/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }

    response = self.doPost('/udj/0_6/players/1/location', newLocation)
    self.assertEqual(response.status_code, 200)
    playerLocation = PlayerLocation.objects.get(player__id=1)
    self.assertEqual(newLocation['address'], playerLocation.address)
    self.assertEqual(newLocation['locality'], playerLocation.locality)
    self.assertEqual(newLocation['region'], playerLocation.region)
    self.assertEqual(newLocation['postal_code'], playerLocation.postal_code)
    self.assertEqual(newLocation['country'], playerLocation.country)
    self.assertEqual(-93.4814, playerLocation.point.x)
    self.assertEqual(44.981609, playerLocation.point.y)

  def testSetLocationWithNoPreviousLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }

    response = self.doPost('/udj/0_6/players/4/location', newLocation)
    self.assertEqual(200, response.status_code)
    playerLocation = PlayerLocation.objects.get(player__id=4)
    self.assertEqual(newLocation['address'], playerLocation.address)
    self.assertEqual(newLocation['locality'], playerLocation.locality)
    self.assertEqual(newLocation['region'], playerLocation.region)
    self.assertEqual(newLocation['postal_code'], playerLocation.postal_code)
    self.assertEqual(newLocation['country'], playerLocation.country)
    self.assertEqual(-93.4814, playerLocation.point.x)
    self.assertEqual(44.981609, playerLocation.point.y)

  def testSetSortingAlgorithm(self):
    algorithmParams = {
      'sorting_algorithm_id' : '2'
    }
    response = self.doPost('/udj/0_6/players/1/sorting_algorithm', algorithmParams)
    self.assertEqual(200, response.status_code, response.content)
    player = Player.objects.get(pk=1)
    self.assertEqual(2, player.sorting_algo.id)

  def testAddAdmin(self):
    response = self.doPut('/udj/0_6/players/1/admins/7')
    self.assertEqual(201, response.status_code)
    self.assertTrue(PlayerAdmin.objects.filter(admin_user__id=7, player__id=1).exists())

  def testNonExistentAdminAdd(self):
    response = self.doPut('/udj/0_6/players/1/admins/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testRemoveAdmin(self):
    response = self.doDelete('/udj/0_6/players/1/admins/1')
    self.assertEqual(200, response.status_code)
    self.assertFalse(PlayerAdmin.objects.filter(admin_user__id=1, player__id=1).exists())

  def testNonExistsentAdminRemove(self):
    response = self.doDelete('/udj/0_6/players/1/admins/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testKickUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/3')
    self.assertEqual(200, response.status_code)
    kickedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, kickedUser.kick_flag)

  def testKickNonParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testKickNonExistentUser(self):
    response = self.doPut('/udj/0_6/players/1/kicked_users/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testBanParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/3')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonParticipatingUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/1')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=1, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonExistentUser(self):
    response = self.doPut('/udj/0_6/players/1/banned_users/10000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/8')
    self.assertEqual(200, response.status_code)
    bannedUser = Participant.objects.get(user__id=8, player__id=1)
    self.assertEqual(False, bannedUser.ban_flag)

  def testUnbanNonParticipatingUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanNonExistentUser(self):
    response = self.doDelete('/udj/0_6/players/1/banned_users/1000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testGetBannedUsers(self):
    response = self.doGet('/udj/0_6/players/1/banned_users')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    bannedUsers = json.loads(response.content)
    self.assertEqual(1, len(bannedUsers))
    self.assertEqual('8', bannedUsers[0]['id'])

  def testChangeSongSetPermissionToYes(self):
    playerToChange = Player.objects.get(pk=1)
    playerToChange.allow_user_songset = False
    playerToChange.save()
    self.assertFalse(Player.objects.get(pk=1).allow_user_songset)
    response = self.doPost('/udj/0_6/players/1/songset_user_permission', {'songset_user_permission' : 'yes'})
    self.assertEqual(response.status_code, 200, 'Error: ' + response.content)
    self.assertTrue(Player.objects.get(pk=1).allow_user_songset)

  def testChangeSongSetPerimssionToNo(self):
    self.assertTrue(Player.objects.get(pk=1).allow_user_songset)
    response = self.doPost('/udj/0_6/players/1/songset_user_permission', {'songset_user_permission' : 'no'})
    self.assertEqual(response.status_code, 200, 'Error: ' + response.content)
    self.assertFalse(Player.objects.get(pk=1).allow_user_songset)

  def testBadChangeSongSetPermission(self):
    response = self.doPost('/udj/0_6/players/1/songset_user_permission', {'songset_user_permission' : 'derp'})
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.content, 'Invalid permission value')



class PasswordAdministrationTests(DoesServerOpsTestCase):

  def testChangePassword(self):
    oldTime = PlayerPassword.objects.get(player__id=3).time_set
    newPassword = "nudepassword"
    response = self.doPost('/udj/0_6/players/3/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=3)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))
    self.assertTrue(oldTime < playerPassword.time_set)

  def testDeletePassword(self):
    response = self.doDelete('/udj/0_6/players/3/password')
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.filter(player__id=3)
    self.assertFalse(playerPassword.exists())

class CurrentSongTestCase(DoesServerOpsTestCase):

  def testSetCurrentSong(self):
    response = self.doPost('/udj/0_6/players/1/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('FN',ActivePlaylistEntry.objects.get(pk=5).state)
    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=1).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=1)

  def testRemoveCurrentSong(self):
    response = self.doDelete('/udj/0_6/players/1/current_song')
    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual('FN',ActivePlaylistEntry.objects.get(pk=5).state)
    self.assertFalse(ActivePlaylistEntry.objects.filter(song__library__id=1, state='PL').exists())


class BlankCurrentSongTestCase(DoesServerOpsTestCase):

  def testSetCurrentSongWithBlank(self):
    response = self.doPost('/udj/0_6/players/3/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=8).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=8)

  def testRemoveWithNoCurrentSong(self):
    response = self.doDelete('/udj/0_6/players/3/current_song')
    self.assertEqual(response.status_code, 404, response.content)
    self.assertEqual('song', response[MISSING_RESOURCE_HEADER])


class PlaylistModTests(DoesServerOpsTestCase):
  def testBasicSongRemove(self):
    response = self.doDelete('/udj/0_6/players/1/active_playlist/songs/2')
    self.assertEqual(response.status_code, 200)

    shouldBeRemoved = ActivePlaylistEntry.objects.get(pk=2)
    self.assertEqual('RM', shouldBeRemoved.state)

  def testPlaylistMultiMod(self):
    toAdd = [9]
    toRemove = [3]

    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(response.status_code, 200, response.content)
    #make sure song was queued
    addedSong = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=9, state='QE')
    #make sure song was removed
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__player__id=1,
      song__player_lib_song_id=3,
      state='QE').exists())
    self.assertTrue(ActivePlaylistEntry.objects.filter(
      song__player__id=1,
      song__player_lib_song_id=3,
      state='RM').exists())

  def testBadRemoveMultiMod(self):
    toAdd = [9]
    toRemove = [3,6]

    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(response.status_code, 404, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

    responseJSON = json.loads(response.content)
    self.assertEqual([6], responseJSON)

    #ensure 9 wasn't added
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__player__id='1',
      song__player_lib_song_id='9',
      state="QE").exists())

    #ensure 3 is still queued
    ActivePlaylistEntry.objects.get(
      song__player__id='1',
      song__player_lib_song_id='3',
      state="QE")

  def testDuplicateAddMultiMod(self):
    sixInitVoteCount = len(ActivePlaylistEntry.objects.get(song__player__id=1, song__player_lib_song_id=6).upvoters())

    toAdd = [6,9]
    toRemove = [3]
    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(200, response.status_code, response.content)

    #ensure 9 was added
    self.assertTrue(ActivePlaylistEntry.objects.filter(
      song__player__id='1',
      song__player_lib_song_id='9',
      state="QE").exists())

    #ensure 3 is no longer queued
    ActivePlaylistEntry.objects.get(
      song__player__id='1',
      song__player_lib_song_id='3',
      state="RM")

    #ensure the vote count for 6 hasn't changed since it's the current song.
    sixNewVoteCount = len(ActivePlaylistEntry.objects.get(song__player__id=1, song__player_lib_song_id=6).upvoters())
    self.assertEqual(sixInitVoteCount, sixNewVoteCount)

class LibTestCases(DoesServerOpsTestCase):

  def verifySongAdded(self, jsonSong):
    addedSong = LibraryEntry.objects.get(library__id=1, lib_id=jsonSong['id'])
    self.assertEqual(addedSong.title, jsonSong['title'])
    self.assertEqual(addedSong.artist, jsonSong['artist'])
    self.assertEqual(addedSong.album, jsonSong['album'])
    self.assertEqual(addedSong.track, jsonSong['track'])
    self.assertEqual(addedSong.genre, jsonSong['genre'])
    self.assertEqual(addedSong.duration, jsonSong['duration'])

  def testSimpleAdd(self):
    payload = [{
      "id" : "11",
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }]

    response = self.doJSONPut('/udj/0_6/players/1/library/songs', json.dumps(payload))
    self.assertEqual(201, response.status_code, response.content)
    self.verifySongAdded(payload[0])

  def testDuplicateAdd(self):
    payload = [{
      "id" : "10",
      "title" : "My Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skrillex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }]

    response = self.doJSONPut('/udj/0_6/players/1/library/songs', json.dumps(payload))
    self.assertEqual(201, response.status_code, response.content)

  def testBadDuplicateAdd(self):
    payload = [{
      "id" : "10",
      "title" : "Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skirllex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }]

    response = self.doJSONPut('/udj/0_6/players/1/library/songs', json.dumps(payload))
    self.assertEqual(409, response.status_code, response.content)


  def testDelete(self):
    response = self.doDelete('/udj/0_6/players/1/library/10')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=10).is_deleted)

  def testDeleteOnPlaylist(self):
    response = self.doDelete('/udj/0_6/players/1/library/5')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=5).is_deleted)
    self.assertEqual(u'RM', ActivePlaylistEntry.objects.get(pk=4).state)

  def testBadDelete(self):
    response = self.doDelete('/udj/0_6/players/1/library/12')
    self.assertEqual(404, response.status_code, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')


  def testMultiMod(self):
    to_add = [{
      "id" : "11",
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }]

    to_delete = [1,2]

    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(200, response.status_code, response.content)
    self.verifySongAdded(to_add[0])
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=1).is_deleted)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=2).is_deleted)

  def testDuplicateMultiModAdd(self):
    to_add = [{
      "id": "2",
      "title": "Narcolepsy",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 2,
      "genre": "Rock",
      "duration": 228,
    },
    {
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    } 
    ]
    to_delete=[]
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(200, response.status_code, response.content)
    #Make sure fuel got inserted.
    fuel = LibraryEntry.objects.get(library__id=1, lib_id='11')


  def testBadDuplicateMultiModAdd(self):
    to_add = [{
      "id": "1",
      "title": "Semi-Charmed Life",
      "artist": "Third Eye Blind",
      "album": "blah",
      "track": 3,
      "genre": "Rock",
      "duration": 268
    },
    {
      "id": "2",
      "title": "Narcolepsy",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 2,
      "genre": "Rock",
      "duration": 228,
    },
    {
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    } 
    ]
    to_delete=[]
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(409, response.status_code, response.content)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(['1'], jsonResponse)
    #Make sure we didn't add fuel because this was a bad one
    self.assertFalse(LibraryEntry.objects.filter(library__id=1, lib_id=11).exists())


  def testBadMultiModRemove(self):
    to_add = [{
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    }
    ]
    to_delete=['1','14']
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(404, response.status_code, response.content)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(['14'], jsonResponse, jsonResponse)
    #Make sure we didn't add Fuel because this was a bad one
    self.assertFalse(LibraryEntry.objects.filter(library__id=1, lib_id=11).exists())
    #Make sure we didn't delete Semi-Charmed Life because this request was bad
    self.assertTrue(LibraryEntry.objects.filter(library__id=1, lib_id=1, is_deleted=False).exists())


class BanTestCases(DoesServerOpsTestCase):

  def testAddSong2BanList(self):
    response = self.doPut('/udj/0_6/players/1/ban_music/1')
    player = Player.objects.get(pk=1)
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=1).is_banned(player), True)

  def testUnbanSong(self):
    response = self.doDelete('/udj/0_6/players/1/ban_music/4')
    player = Player.objects.get(pk=1)
    if response.has_header(MISSING_RESOURCE_HEADER):
      errmsg = response[MISSING_RESOURCE_HEADER]
      self.assertEqual(200, response.status_code, errmsg)
    else:
      self.assertEqual(200, response.status_code)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=4).is_banned(player), False)

  def testBadSongBan(self):
    response = self.doDelete('/udj/0_6/players/1/ban_music/12')
    player = Player.objects.get(pk=1)
    self.assertEqual(404, response.status_code, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  def testMultiBan(self):
    toBan = [1]
    toUnban = [4]
    response = self.doPost('/udj/0_6/players/1/ban_music', {'to_ban' : json.dumps(toBan), 
      'to_unban' : json.dumps(toUnban)})
    player = Player.objects.get(pk=1)
    if response.has_header(MISSING_RESOURCE_HEADER):
      errmsg = response[MISSING_RESOURCE_HEADER]
      self.assertEqual(200, response.status_code, errmsg)
    else:
      self.assertEqual(200, response.status_code)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=1).is_banned(player), True)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=4).is_banned(player), False)

  def testDuplicateBan(self):
    response = self.doPut('/udj/0_6/players/1/ban_music/4')
    player = Player.objects.get(pk=1)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=4).is_banned(player), True)

  def testDuplicateMultiBan(self):
    toBan = [1,4]
    toUnban = []
    response = self.doPost('/udj/0_6/players/1/ban_music', {'to_ban' : json.dumps(toBan), 
      'to_unban' : json.dumps(toUnban)})
    player = Player.objects.get(pk=1)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=1).is_banned(player), True)
    self.assertEqual(LibraryEntry.objects.get(library__id=1, lib_id=4).is_banned(player), True)




class KurtisTestCase(DoesServerOpsTestCase):
  username = "kurtis"
  userpass = "testkurtis"

class JeffTestCase(DoesServerOpsTestCase):
  username = "jeff"
  userpass = "testjeff"

class YunYoungTestCase(DoesServerOpsTestCase):
  username = "yunyoung"
  userpass = "testyunyoung"

class AlejandroTestCase(DoesServerOpsTestCase):
  username = "alejandro"
  userpass = "testalejandro"

class LucasTestCase(DoesServerOpsTestCase):
  username = "lucas"
  userpass = "testlucas"

class LeeTestCase(DoesServerOpsTestCase):
  username = "lee"
  userpass = "testlee"

class ZachTestCase(DoesServerOpsTestCase):
  username = "zach"
  userpass = "testzach"

class MattTestCase(DoesServerOpsTestCase):
  username = "matt"
  userpass = "testmatt"

class EnsureActiveJeffTest(JeffTestCase):
  def setUp(self):
    super(EnsureActiveJeffTest, self).setUp()
    jeff = Participant.objects.get(user__id=3, player__id=1)
    jeff.time_last_interaction = datetime.now()
    jeff.save()

