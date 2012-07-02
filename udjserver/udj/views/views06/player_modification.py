import json

from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Player
from udj.models import PlayerPassword
from udj.exceptions import LocationNotFoundError
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import PlayerExists
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.authdecorators import IsOwnerOrAdmin
from udj.views.views06.authdecorators import NeedsAuth

from udj.views.views06.helpers import setPlayerLocation


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
  if Player.objects.filter(owning_user__id=user_id, name=givenName).exists():
    return HttpResponse(status=409)

  player.name=givenName
  player.save()

  return HttpResponse()

@csrf_exempt
@AcceptsMethods(['POST', 'DELETE'])
@NeedsAuth
@IsOwnerOrAdmin
@PlayerExists
def modifyPlayerPassword(request, player_id, player):
  if request.method == 'POST':
    return setPlayerPassword(request, user_id, player_id, player)
  elif request.method == 'DELETE':
    return deletePlayerPassword(request, user_id, player_id, player)

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

def deletePlayerPassword(request, user_id, player_id, player):
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
@IsOwnerOrAdmin
@PlayerExists
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

  return HttpRequest()
