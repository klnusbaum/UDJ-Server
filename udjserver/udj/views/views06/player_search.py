import json

from udj.models import PlayerLocation
from udj.models import Player
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse
from udj.headers import NOT_ACCEPTABLE_REASON_HEADER

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import HttpRequest
from django.http import HttpResponse

from settings import default_search_radius, max_search_radius, min_search_radius

@NeedsAuth
@AcceptsMethods(['GET'])
def getNearbyPlayers(request, latitude, longitude):

  search_limit = int(request.GET.get('max_results', 20))
  search_limit = min(search_limit, 100)

  search_radius = int(request.GET.get('radius', default_search_radius))
  if search_radius >= max_search_radius or search_radius < min_search_radius:
    radii_info = { 'min_radius' : min_search_radius, 'max_radius' : max_search_radius}
    toReturn = HttpJSONResponse(json.dumps(radii_info), status=406)
    toReturn[NOT_ACCEPTABLE_REASON_HEADER] = 'bad-radius'
    return toReturn

  givenLat = float(latitude)
  givenLon = float(longitude)
  point = Point(givenLon, givenLat)

  nearbyLocations = PlayerLocation.objects.exclude(player__state='IN').filter(
    point__distance_lte=(point, D(km=search_radius))).distance(point).order_by('distance')[:search_limit]

  nearbyPlayers = [location.player for location in nearbyLocations]

  return HttpJSONResponse(json.dumps(nearbyPlayers, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
@HasNZParams(['name'])
def getPlayers(request):
  search_limit = int(request.GET.get('max_results', 20))
  search_limit = min(search_limit, 100)

  players = Player.objects.filter(name__icontains=request.GET['name']).exclude(state='IN')[:search_limit]
  return HttpJSONResponse(json.dumps(players, cls=UDJEncoder))

