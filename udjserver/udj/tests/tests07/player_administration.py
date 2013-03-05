import json

from udj.models import PlayerPermission
from udj.models import PlayerPermissionGroup
from udj.models import Library, AssociatedLibrary
from udj.models import Player
from udj.models import PlayerPassword
from udj.models import PlayerLocation
from udj.models import ActivePlaylistEntry
from udj.models import Participant
from udj.models import hashPlayerPassword
from udj.testhelpers.tests07.testclasses import KurtisTestCase
from udj.headers import FORBIDDEN_REASON_HEADER, MISSING_RESOURCE_HEADER


class DefaultOwnerAdminTests(KurtisTestCase):

  def testGetEnabledLibraries(self):
    response = self.doGet('/players/1/enabled_libraries')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    returned_libraries = json.loads(response.content)
    actual_libraries = Player.objects.get(pk=1).EnabledLibraries
    self.assertEqual(len(actual_libraries), len(returned_libraries))
    for returned_library in returned_libraries:
      actual_library = actual_libraries.get(pk=returned_library['id'])
      self.assertEqual(actual_library.name, returned_library['name'])
      self.assertEqual(actual_library.description, returned_library['description'])
      self.assertEqual(actual_library.pub_key, returned_library['pub_key'])
      self.assertEqual(actual_library.get_read_permission_display(),
                       returned_library['read_permission'])
      self.assertEqual(actual_library.get_write_permission_display(),
                       returned_library['write_permission'])


  def testEnableGoodLibrary(self):
    response = self.doPut('/players/1/enabled_libraries/8')
    self.assertEqual(200, response.status_code)
    self.assertTrue(
        AssociatedLibrary.objects.filter(player__id=1, library__id=8, enabled=True).exists())


  def testEnableUnauthorizedLibrary(self):
    response = self.doPut('/players/1/enabled_libraries/9')
    self.assertEqual(403, response.status_code)
    self.assertEqual('library-permission', response[FORBIDDEN_REASON_HEADER])

  def testEnableNonExistentLibrary(self):
    response = self.doPut('/players/1/enabled_libraries/949949949')
    self.assertEqual(404, response.status_code)
    self.assertEqual('library', response[MISSING_RESOURCE_HEADER])

  def testDisableLibrary(self):
    response = self.doDelete('/players/1/enabled_libraries/1')
    self.assertEqual(200, response.status_code)
    self.assertFalse(AssociatedLibrary.objects.get(player__id=1, library__id=1).enabled)
    self.assertFalse(ActivePlaylistEntry.objects.filter(player__id=1,
                                                        song__library__id=1,
                                                        state=u'QE').exists())

  def testDoubleDisableLibrary(self):
    response = self.doDelete('/players/1/enabled_libraries/1')
    self.assertEqual(200, response.status_code)
    response = self.doDelete('/players/1/enabled_libraries/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('library', response[MISSING_RESOURCE_HEADER])

  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testRemovePassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/players/1/password', {'password': newPassword})
    self.assertTrue(Player.objects.get(pk=1).HasPassword)
    response = self.doDelete('/players/1/password')
    self.assertFalse(Player.objects.get(pk=1).HasPassword)


  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }

    response = self.doPost('/players/1/location', newLocation)
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
    PlayerLocation.objects.get(player__id=1).delete()

    newLocation = {
      'address' : '305 Vicksburg Lane',
      'locality' : 'Plymouth',
      'region' : 'MN',
      'postal_code' : '55447',
      'country' : 'U.S.'
    }

    response = self.doPost('/players/1/location', newLocation)
    self.assertEqual(200, response.status_code)
    playerLocation = PlayerLocation.objects.get(player__id=1)
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
    response = self.doPost('/players/1/sorting_algorithm', algorithmParams)
    self.assertEqual(200, response.status_code, response.content)
    player = Player.objects.get(pk=1)
    self.assertEqual(2, player.sorting_algo.id)

  def testSetPlayerPlaying(self):
    player = Player.objects.get(pk=1)
    player.state = u'PA'
    player.save()
    response = self.doPost('/players/1/state', {'state' :'playing'})
    self.assertEqual(200, response.status_code)
    self.assertEqual(u'PL', Player.objects.get(pk=1).state)

  def testPausePlayer(self):
    response = self.doPost('/players/1/state', {'state' :'paused'})
    self.assertEqual(200, response.status_code)
    self.assertEqual(u'PA', Player.objects.get(pk=1).state)

  def testSetPlayerInactive(self):
    response = self.doPost('/players/1/state', {'state' :'inactive'})
    self.assertEqual(200, response.status_code)
    self.assertEqual(u'IN', Player.objects.get(pk=1).state)

  def testBadPlayerStateSet(self):
    response = self.doPost('/players/1/state', {'state' :'bad'})
    self.assertEqual(400, response.status_code)
    self.assertEqual(u'PL', Player.objects.get(pk=1).state)

  def testSetVolume(self):
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)
    response = self.doPost('/players/1/volume', {'volume' : 2})
    self.assertEqual(response.status_code, 200)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 2)

  def testBadVolumeSet(self):
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)
    response = self.doPost('/players/1/volume', {'volume' : 11})
    self.assertEqual(response.status_code, 400)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.volume, 5)

  def testKickUser(self):
    response = self.doPut('/players/1/kicked_users/3')
    self.assertEqual(200, response.status_code)
    kickedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, kickedUser.kick_flag)

  def testKickNonParticipatingUser(self):
    response = self.doPut('/players/1/kicked_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testKickNonExistentUser(self):
    response = self.doPut('/players/1/kicked_users/100000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testBanParticipatingUser(self):
    response = self.doPut('/players/1/banned_users/3')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=3, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonParticipatingUser(self):
    response = self.doPut('/players/1/banned_users/1')
    self.assertEqual(201, response.status_code)
    bannedUser = Participant.objects.get(user__id=1, player__id=1)
    self.assertEqual(True, bannedUser.ban_flag)

  def testBanNonExistentUser(self):
    response = self.doPut('/players/1/banned_users/10000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanUser(self):
    response = self.doDelete('/players/1/banned_users/8')
    self.assertEqual(200, response.status_code)
    bannedUser = Participant.objects.get(user__id=8, player__id=1)
    self.assertEqual(False, bannedUser.ban_flag)

  def testUnbanNonParticipatingUser(self):
    response = self.doDelete('/players/1/banned_users/1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testUnbanNonExistentUser(self):
    response = self.doDelete('/players/1/banned_users/1000000')
    self.assertEqual(404, response.status_code)
    self.assertEqual('user', response[MISSING_RESOURCE_HEADER])

  def testGetBannedUsers(self):
    response = self.doGet('/players/1/banned_users')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    bannedUsers = json.loads(response.content)
    self.assertEqual(1, len(bannedUsers))
    self.assertEqual('8', bannedUsers[0]['id'])


  def testGetPermissions(self):
    response = self.doGet('/players/1/permissions')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    permissions = json.loads(response.content)
    for perm in permissions.keys():
      perm_code = PlayerPermission.PERMISSION_NAME_MAP[perm]
      actual_perm_groups = (PlayerPermission.objects.filter(player__id=1, permission=perm_code)
                                             .values_list('group__name', flat=True))
      returned_perm_groups = permissions[perm]
      self.assertEqual(len(actual_perm_groups), len(returned_perm_groups))
      for group in actual_perm_groups:
        self.assertTrue(group in returned_perm_groups)

  def testAddPermission(self):
    response = self.doPut('/players/1/permissions/set_sorting_algorithm/empty_test1')
    self.assertEqual(200, response.status_code)

    test_perm1 = PlayerPermission.objects.filter(player__id=1,
                                                 permission=u'SSA',
                                                 group__name=u'empty_test1')
    self.assertTrue(test_perm1.exists())


  def testAddBadPermission(self):
    response = self.doPut('/players/1/permissions/invalid_perm/empty_test1')
    self.assertEqual(404, response.status_code)
    self.assertEqual('permission', response[MISSING_RESOURCE_HEADER])

  def testAddPermissionWithBadGroup(self):
    self.assertTrue(Player.objects.filter(pk=1).exists())
    response = self.doPut('/players/1/permissions/set_sorting_algorithm/dontexists_mofo')
    self.assertEqual(404, response.status_code)
    self.assertEqual('permission-group', response[MISSING_RESOURCE_HEADER])

    self.assertFalse(PlayerPermission.objects.filter(player__id=1,
                                                     permission=u'SSA',
                                                     group__name=u'empty_test1').exists())


  def testRemovePermission(self):
    response = self.doDelete('/players/1/permissions/set_sorting_algorithm/owner')
    self.assertEqual(200, response.status_code)
    self.assertFalse(PlayerPermission.objects.filter(player__id=1,
                                                     permission=u'SSA',
                                                     group__name=u'owner').exists())

  def testRemoveBadPermission(self):
    response = self.doDelete('/players/1/permissions/invalid/owner')
    self.assertEqual(404, response.status_code)
    self.assertEqual('permission', response[MISSING_RESOURCE_HEADER])

  def testRemovePermissionWithBadGroup(self):
    response = self.doPut('/players/1/permissions/set_sorting_algorithm/dontexists_mofo')
    self.assertEqual(404, response.status_code)
    self.assertEqual('permission-group', response[MISSING_RESOURCE_HEADER])

  def testGetPermissionGroups(self):
    response = self.doGet('/players/1/permission_groups')
    self.assertEqual(200, response.status_code)
    self.isJSONResponse(response)
    retrieved_groups = json.loads(response.content)
    actual_groups = PlayerPermissionGroup.objects.filter(player__id=1)
    self.assertEqual(len(actual_groups), len(retrieved_groups))
    for group in retrieved_groups:
      current_actual_group = actual_groups.get(name=group['name'])
      current_actual_members = current_actual_group.Members
      self.assertEqual(len(current_actual_members), len(group['users']))
      for user in group['users']:
        existing_user  =current_actual_members.get(pk=user['id'])



