import json


from udj.models import Player
from udj.models import Participant
from udj.models import SortingAlgorithm
from udj.models import PlayerLocation
from udj.models import PlayerPermission
from udj.models import PlayerPermissionGroup
from udj.views.views07.authdecorators import NeedsAuth, HasPlayerPermissions
from udj.views.views07.decorators import AcceptsMethods, PlayerExists, LibraryExists, HasNZJSONParams, NeedsJSON
from udj.views.views07.responses import HttpJSONResponse
from udj.views.views07.responses import HttpResponseForbiddenWithReason
from udj.views.views07.responses import HttpResponseMissingResource
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.exceptions import LocationNotFoundError

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.db import transaction
from django.db import IntegrityError

from settings import geocodeLocation

@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
def getEnabledLibraries(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.EnabledLibraries, cls=UDJEncoder))

@HasPlayerPermissions(['ELI'])
def enable_library(request, player, library):
  if library.user_has_read_perm(player.owning_user):
    player.enable_library(library)
    return HttpResponse()
  else:
    return HttpResponseForbiddenWithReason('library-permission')

@HasPlayerPermissions(['DLI'])
def disable_library(request, player, library):
  try:
    player.disable_library(library)
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('library')

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@LibraryExists
def modEnabledLibraries(request, player_id, library_id, player, library):
  if request.method == 'PUT':
    return enable_library(request, player, library)
  else:
    return disable_library(request, player, library)



@HasPlayerPermissions(['SPA'])
@NeedsJSON
@HasNZJSONParams(['password'])
def setPlayerPassword(request, player, json_params):
  player.setPassword(json_params['password'])
  return HttpResponse()

@HasPlayerPermissions(['SPA'])
def deletePlayerPassword(request, player):
  try:
    player.removePassword()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('password')


@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@PlayerExists
def modifyPlayerPassword(request, player_id, player):
  if request.method == 'POST':
    return setPlayerPassword(request, player)
  elif request.method == 'DELETE':
    return deletePlayerPassword(request, player)


@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@PlayerExists
@HasPlayerPermissions(['SLO'])
def modLocation(request, player_id, player):
  if request.method == 'POST':
    return setLocation(request, player)
  else:
    return deleteLocation(request, player)


def deleteLocation(request, player):
  try:
    PlayerLocation.objects.get(player=player).delete()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('location')

@NeedsJSON
@HasNZJSONParams(['postal_code', 'country'])
def setLocation(request, player, json_params):
  postal_code = json_params['postal_code']
  country = json_params['country']
  address = json_params.get('address', "")
  locality = json_params.get('locality',"")
  region = json_params.get('region', "")

  try:
    lat, lon = geocodeLocation(postal_code, country, address, locality, region)
  except LocationNotFoundError as e:
    return HttpResponseBadRequest('Location not found')

  playerLocation, created = PlayerLocation.objects.get_or_create(player=player,
                                                                  defaults={
                                                                    'point' : Point(lon, lat),
                                                                    'address' : address,
                                                                    'locality' : locality,
                                                                    'region' : region,
                                                                    'country' : country,
                                                                    'postal_code' : postal_code
                                                                    }
                                                                  )
  if not created:
    playerLocation.point = Point(lon, lat)
    playerLocation.address = address
    playerLocation.locality = locality
    playerLocation.region = region
    playerLocation.country = country
    playerLocation.postal_code = postal_code
    playerLocation.save()


  return HttpResponse()

@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsAuth
@PlayerExists
@HasPlayerPermissions(['SSA'])
@NeedsJSON
@HasNZJSONParams(['sorting_algorithm_id'])
def setSortingAlgorithm(request, player_id, player, json_params):
  try:
    newAlgorithm = SortingAlgorithm.objects.get(pk=json_params['sorting_algorithm_id'])
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('sorting-algorithm')

  player.sorting_algo = newAlgorithm
  player.save()
  return HttpResponse()

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@PlayerExists
@HasPlayerPermissions(['SPT'])
@NeedsJSON
@HasNZJSONParams(['state'])
def setPlayerState(request, player_id, player, json_params):
  givenState = json_params['state']

  if givenState == u'paused':
    player.state = u'PA'
  elif givenState == u'playing':
    player.state = u'PL'
  elif givenState == u'inactive':
    player.state = u'IN'
  else:
    return HttpResponseBadRequest("Bad state given: " + givenState)

  player.save()
  return HttpResponse()

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@PlayerExists
@HasPlayerPermissions(['CVO'])
@NeedsJSON
@HasNZJSONParams(['volume'])
def setPlayerVolume(request, player_id, player, json_params):
  try:
    newVolume = int(json_params['volume'])
    if newVolume > 10 or newVolume < 0:
      return HttpResponseBadRequest()
    player.volume = newVolume
    player.save()
    return HttpResponse()
  except ValueError:
    return HttpResponseBadRequest('Bad volume: ' + json_params['volume'])

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT'])
@PlayerExists
@HasPlayerPermissions(['KUS'])
def kickUser(request, player_id, kick_user_id, player):
  try:
    toKick = Participant.objects.get(user__id=kick_user_id, player=player)
    toKick.kick_flag=True
    toKick.save()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('user')





@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@HasPlayerPermissions(['BUS'])
def modBans(request, player_id, ban_user_id, player):
  if request.method == 'PUT':
    return banUser(request, player_id, ban_user_id, player)
  elif request.method == 'DELETE':
    return unbanUser(request, player_id, ban_user_id, player)


def banUser(request, player_id, ban_user_id, player):
  try:
    user = User.objects.get(pk=ban_user_id)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('user')

  bannedParticipant, created = Participant.objects.get_or_create(user=user, player=player,
      defaults={'ban_flag' : True})
  if not created:
    bannedParticipant.ban_flag = True
    bannedParticipant.save()

  return HttpResponse(status=201)

def unbanUser(request, player_id, ban_user_id, player):
  try:
    bannedUser = Participant.objects.get(user__id=ban_user_id, player=player)
    bannedUser.ban_flag=False
    bannedUser.save()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('user')

@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
def getBannedUsers(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.BannedUsers, cls=UDJEncoder))


@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
def getPlayerPermissions(request, player_id, player):
  permissions = {}
  for perm in PlayerPermission.PERMISSION_CHOICES:
    perm_groups = (PlayerPermission.objects.filter(player=player, permission=perm[0])
                                           .values_list('group__name', flat=True))
    permissions[perm[1]] = perm_groups
  return HttpJSONResponse(json.dumps(permissions, cls=UDJEncoder))

def addPermissions(player, perm_code, group_name):
  try:
    actual_group = PlayerPermissionGroup.objects.get(player=player, name=group_name)
    PlayerPermission.objects.get_or_create(player=player,
                                           permission=perm_code,
                                           group=actual_group)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('permission-group')

  return HttpResponse()


def removePermissions(player, perm_code, group_name):
  try:
    PlayerPermission.objects.get(player=player,
                                 permission=perm_code,
                                 group__name=group_name).delete()
  except ObjectDoesNotExist:
    transaction.rollback()
    return HttpResponseMissingResource('permission-group')
  transaction.commit()
  return HttpResponse()


@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@HasPlayerPermissions(['MPE'])
def modPlayerPermissions(request, player_id, permission_name, group_name, player):
  try:
    perm_code = PlayerPermission.PERMISSION_NAME_MAP[permission_name]
  except KeyError:
    return HttpResponseMissingResource('permission')

  if request.method == 'PUT':
    return addPermissions(player, perm_code, group_name)
  else:
    return removePermissions(player, perm_code, group_name)


@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
def getPermissionGroups(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.PermissionGroups, cls=UDJEncoder))



def addPlayerPermissionGroup(player, group_name):
  try:
    PlayerPermissionGroup(player=player, name=group_name).save()
    return HttpResponse(status=201)
  except IntegrityError:
    return HttpResponse(status=409)

def removePlayerPermissionGroup(player, group_name):
  try:
    PlayerPermissionGroup.objects.get(player=player, name=group_name).delete()
    return HttpResponse(status=200)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('permission-group')


@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@HasPlayerPermissions(['MPE'])
def modPlayerPermissionGroup(request, player_id, group_name, player):
  if request.method == 'PUT':
    return addPlayerPermissionGroup(player, group_name)
  else:
    return removePlayerPermissionGroup(player, group_name)


@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
def getPermissionGroupMembers(request, player_id, group_name, player):
  try:
    group = PlayerPermissionGroup.objects.get(player=player, name=group_name)
    return HttpJSONResponse(json.dumps(group.Members, cls=UDJEncoder))
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('permission-group')

@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
def modPermissionGroupMembers(request, player_id, group_name, user_id, player):
  try:
    user = User.objects.get(pk=user_id)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('user')

  try:
    group = PlayerPermissionGroup.objects.get(player=player, name=group_name)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('permission-group')

  if request.method == 'PUT':
    group.add_member(user)
    return HttpResponse(status=201)
  else:
    try:
      group.remove_member(user)
      return HttpResponse()
    except ObjectDoesNotExist:
      return HttpResponseMissingResource('user')

