import json

from settings import default_sorting_algo
from udj.headers import MISSING_RESOURCE_HEADER

from udj.models import Player
from udj.models import ExternalLibrary
from udj.models import SortingAlgorithm
from udj.models import PlayerPassword
from udj.exceptions import LocationNotFoundError
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.auth import hashPlayerPassword
from udj.views.views06.auth import getUserForTicket
from udj.views.views06.helpers import setPlayerLocation
from udj.views.views06.helpers import HttpJSONResponse
from udj.views.views06.JSONCodecs import UDJEncoder

from django.db import transaction
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist

def isValidLocation(location):
  return 'postal_code' in location and 'country' in location

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT'])
@NeedsJSON
@transaction.commit_on_success
def createPlayer(request):
  user = getUserForTicket(request)
  try:
    newPlayerJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  #Ensure the name attribute was provided with the JSON
  try:
    newPlayerName = newPlayerJSON['name']
  except KeyError:
    return HttpResponseBadRequest('No name given')

  #Determine which sorting algorithm to use
  if 'sorting_algorithm_id' in newPlayerJSON:
    try:
      sortingAlgo = SortingAlgorithm.objects.get(pk=newPlayerJSON['sorting_algorithm_id'])
    except ObjectDoesNotExist:
      toReturn = HttpResponseNotFound()
      toReturn[MISSING_RESOURCE_HEADER] = 'sorting_algorithm'
      return toReturn
  else:
    try:
      sortingAlgo = SortingAlgorithm.objects.get(function_name=default_sorting_algo)
    except ObjectDoesNotExist:
      raise ImproperlyConfigured('Default sorting algorithm is not in database')


  #Ensure that the suers doesn't already have a player with the given name
  conflictingPlayer = Player.objects.filter(owning_user=user, name=newPlayerName)
  if conflictingPlayer.exists():
    return HttpResponse('A player with that name already exists', status=409)

  #Create and save new player
  newPlayer = Player(
      owning_user=user,
      name=newPlayerName,
      sorting_algo=sortingAlgo)
  newPlayer.save()

  #If password provided, create and save password
  if 'password' in newPlayerJSON:
    PlayerPassword(player=newPlayer, password_hash=hashPlayerPassword(newPlayerJSON['password'])).save()

  #If locaiton provided, geocode it and save it
  if 'location' in newPlayerJSON:
    location = newPlayerJSON['location']
    if isValidLocation(location):
      try:
        setPlayerLocation(location, newPlayer)
      except LocationNotFoundError:
        return HttpResponseBadRequest('Location not found')
    else:
      return HttpResponseBadRequest('Bad location')

  return HttpJSONResponse(json.dumps(newPlayer, cls=UDJEncoder), status=201)

