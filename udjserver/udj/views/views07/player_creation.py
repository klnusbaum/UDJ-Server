import json

from settings import DEFAULT_SORTING_ALGO, DEFAULT_PLAYER_PERMISSIONS, geocodeLocation

from udj.models import Player
from udj.models import PlayerPermission
from udj.models import PlayerPermissionGroup
from udj.models import SortingAlgorithm
from udj.models import PlayerPassword
from udj.models import PlayerLocation
from udj.exceptions import LocationNotFoundError
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import NeedsJSON
from udj.views.views07.decorators import HasNZJSONParams
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.responses import HttpJSONResponse, HttpResponseMissingResource
from udj.views.views07.JSONCodecs import UDJEncoder

from django.db import transaction
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.gis.geos import Point


def set_default_player_permissions(player, owner_group):
  def create_perm(perm_name):
    new_perm = PlayerPermission(player=player, permission=perm_name, group=owner_group)
    new_perm.save()
  map(create_perm, DEFAULT_PLAYER_PERMISSIONS)

def isValidLocation(location):
  return 'postal_code' in location and 'country' in location

@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT'])
@NeedsJSON
@HasNZJSONParams(['name'])
@transaction.commit_on_success
def createPlayer(request, json_params):
  user = request.udjuser
  newPlayerName = json_params['name']


  #Determine which sorting algorithm to use
  if 'sorting_algorithm_id' in json_params:
    try:
      sortingAlgo = SortingAlgorithm.objects.get(pk=json_params['sorting_algorithm_id'])
    except ObjectDoesNotExist:
      return HttpResponseMissingResource('sorting-algorithm')
  else:
    try:
      sortingAlgo = SortingAlgorithm.objects.get(function_name=DEFAULT_SORTING_ALGO)
    except ObjectDoesNotExist:
      raise ImproperlyConfigured('Default sorting algorithm is not in database')

  #If locaiton provided, attempted to geocode it.
  if 'location' in json_params:
    location = json_params['location']
    if isValidLocation(location):
      try:
        address = location.get('address', "")
        locality = location.get('locality', "")
        region = location.get('region', "")
        postal_code = location['postal_code']
        country = location['country']
        lat, lon = geocodeLocation(postal_code, country, address, locality, region)
      except LocationNotFoundError as e:
        return HttpResponseBadRequest('Location not found. Geocoder error: ' + str(e))
    else:
      return HttpResponseBadRequest('Bad location')


  #Create and save new player
  try:
    newPlayer = Player(owning_user=user,
                       name=newPlayerName,
                       sorting_algo=sortingAlgo)
    newPlayer.save()
  except IntegrityError:
    return HttpResponse('A player with that name already exists', status=409)

  #If password provided, create and save password
  if 'password' in json_params:
    newPlayer.setPassword(json_params['password'])

  #Set location if provided
  if 'location' in json_params:
    playerLocation = PlayerLocation(player=newPlayer,
                                    point=Point(lon, lat),
                                    address=address,
                                    locality=locality,
                                    region=region,
                                    postal_code=postal_code,
                                    country=country)
    playerLocation.save()


  #Create Owner Permissions Group
  owner_group = PlayerPermissionGroup(player=newPlayer, name="owner")
  owner_group.save()
  owner_group.add_member(user)

  #Add owner_group to select permissiosn
  set_default_player_permissions(newPlayer, owner_group)


  return HttpJSONResponse(json.dumps(newPlayer, cls=UDJEncoder), status=201)

