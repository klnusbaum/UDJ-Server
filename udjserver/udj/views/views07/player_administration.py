import json


from udj.models import Player
from udj.models import SortingAlgorithm
from udj.models import PlayerLocation
from udj.views.views07.authdecorators import NeedsAuth, HasPlayerPermissions
from udj.views.views07.decorators import AcceptsMethods, PlayerExists, LibraryExists, HasNZParams
from udj.views.views07.responses import HttpJSONResponse
from udj.views.views07.responses import HttpResponseForbiddenWithReason
from udj.views.views07.responses import HttpResponseMissingResource
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.exceptions import LocationNotFoundError

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point

from settings import geocodeLocation

"""

from udj.models import PlayerPassword
from udj.models import Participant
from udj.models import SortingAlgorithm
from udj.models import PlayerPermission
from udj.models import PlayerPermissionGroup
from udj.exceptions import LocationNotFoundError
from udj.views.views07.auth import hashPlayerPassword

from django.http import HttpRequest
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
"""

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
@HasNZParams(['password'])
def setPlayerPassword(request, player):
  givenPassword = request.POST['password']
  player.setPassword(givenPassword)
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
@HasNZParams(['postal_code', 'country'])
def setLocation(request, player_id, player):
  postal_code = request.POST['postal_code']
  country = request.POST['country']
  address = request.POST.get('address', "")
  locality = request.POST.get('locality',"")
  region = request.POST.get('region', "")

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
@HasNZParams(['sorting_algorithm_id'])
def setSortingAlgorithm(request, player_id, player):
  try:
    newAlgorithm = SortingAlgorithm.objects.get(pk=request.POST['sorting_algorithm_id'])
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('sorting-algorithm')

  player.sorting_algo = newAlgorithm
  player.save()
  return HttpResponse()


"""



@csrf_exempt
@NeedsAuth
@AcceptsMethods(['POST'])
@PlayerExists
@IsOwnerOrAdmin
@HasNZParams(['state'])
def setPlayerState(request, player_id, player):
  givenState = request.POST['state']

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
@IsOwnerOrAdmin
@HasNZParams(['volume'])
def setPlayerVolume(request, player_id, player):
  try:
    newVolume = int(request.POST['volume'])
    if newVolume > 10 or newVolume < 0:
      return HttpResponseBadRequest()
    player.volume = newVolume
    player.save()
    return HttpResponse()
  except ValueError:
    return HttpResponseBadRequest('Bad volume: ' + request.POST['volume'])

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@IsOwnerOrAdmin
def modAdmin(request, player_id, user_id, player):
  if request.method == 'PUT':
    return addAdmin(request, player_id, user_id, player)
  elif request.method == 'DELETE':
    return removeAdmin(request, player_id, user_id, player)

def addAdmin(request, player_id, user_id, player):
  try:
    newAdminUser = User.objects.get(pk=user_id)
    admin_group = PlayerPermissionGroup.objects.get(player=player, name=u'admin')
    admin_group.add_member(newAdminUser)
    return HttpResponse(status=201)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn

def removeAdmin(request, player_id, user_id, player):
  try:
    admin_group = PlayerPermissionGroup.objects.get(player=player, name=u'admin')
    admin_group.remove_member(User.objects.get(pk=user_id))
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT'])
@PlayerExists
@IsOwnerOrAdmin
def kickUser(request, player_id, kick_user_id, player):
  try:
    toKick = Participant.objects.get(user__id=kick_user_id, player=player)
    toKick.kick_flag=True
    toKick.save()
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@IsOwnerOrAdmin
def modBans(request, player_id, ban_user_id, player):
  if request.method == 'PUT':
    return banUser(request, player_id, ban_user_id, player)
  elif request.method == 'DELETE':
    return unbanUser(request, player_id, ban_user_id, player)


def banUser(request, player_id, ban_user_id, player):
  try:
    user = User.objects.get(pk=ban_user_id) 
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn


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
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn

@NeedsAuth
@AcceptsMethods(['GET'])
@PlayerExists
@IsOwnerOrAdmin
def getBannedUsers(request, player_id, player):
  return HttpJSONResponse(json.dumps(player.BannedUsers(), cls=UDJEncoder))

"""
