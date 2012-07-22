import json

from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Player
from udj.models import PlayerPassword
from udj.models import PlayerAdmin
from udj.exceptions import LocationNotFoundError
from udj.views.views06.auth import hashPlayerPassword
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import PlayerExists
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.authdecorators import IsOwnerOrAdmin
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.helpers import setPlayerLocation

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist


@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsAuth
@PlayerExists
@IsOwnerOrAdmin
@HasNZParams(['name'])
def changePlayerName(request, player_id, player):
  givenName = request.POST['name']
  if givenName == '':
    return HttpResponseBadRequest("Bad name")
  if Player.objects.filter(owning_user=player.owning_user, name=givenName).exists():
    return HttpResponse(status=409)

  player.name=givenName
  player.save()

  return HttpResponse()

@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@PlayerExists
@IsOwnerOrAdmin
def modifyPlayerPassword(request, player_id, player):
  if request.method == 'POST':
    return setPlayerPassword(request, player_id, player)
  elif request.method == 'DELETE':
    return deletePlayerPassword(request, player_id, player)

@HasNZParams(['password'])
def setPlayerPassword(request, player_id, player):
  givenPassword = request.POST['password']
  if givenPassword == '':
    return HttpResponseBadRequest("Bad password")

  hashedPassword = hashPlayerPassword(givenPassword)

  playerPassword , created = PlayerPassword.objects.get_or_create(
      player=player,
      defaults={'password_hash': hashedPassword})
  if not created:
    playerPassword.password_hash = hashedPassword
    playerPassword.save()

  return HttpResponse()

def deletePlayerPassword(request, player_id, player):
  try:
    toDelete = PlayerPassword.objects.get(player=player)
    toDelete.delete()
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'password'
    return toReturn

@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@PlayerExists
@IsOwnerOrAdmin
@HasNZParams(['postal_code', 'country'])
def setLocation(request, player_id, player):
  location = {
    'postal_code' : request.POST['postal_code'],
    'country' : request.POST['country']
  }

  location['address'] = request.POST.get('address', None)
  location['locality'] = request.POST.get('locality', None)
  location['region'] = request.POST.get('region', None)

  try:
    setPlayerLocation(location, player)
  except LocationNotFoundError:
    return HttpResponseBadRequest('Location not found')

  return HttpResponse()

@csrf_exempt
@AcceptsMethods(['POST'])
@NeedsAuth
@PlayerExists
@IsOwnerOrAdmin
@HasNZParams(['sorting_algorithm_id'])
def setSortingAlgorithm(request, player_id, player):
  try:
    newAlgorithm = SortingAlgorithm.objects.get(pk=request.POST['sorting_algorithm_id'])
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = "sorting_algorithm"
    return toReturn

  player.sorting_algo = newAlgorithm
  player.save()
  return HttpResponse()


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
def setPlayerVolume(request, user_id, player_id, player):
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
    PlayerAdmin.objects.get_or_create(admin_user=newAdminUser, player=player)
    return HttpResponse(status=201)
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn

def removeAdmin(request, player_id, user_id, player):
  try:
    toRemove = PlayerAdmin.objects.get(admin_user__id=user_id, player=player)
    toRemove.delete()
    return HttpResponse()
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'user'
    return toReturn
