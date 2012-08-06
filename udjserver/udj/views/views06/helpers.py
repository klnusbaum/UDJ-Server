from udj.models import Player
from udj.models import PlayerLocation
from settings import geocodeLocation
from django.http import HttpResponse

from django.contrib.gis.geos import Point

def setPlayerLocation(location, player):
  address = location.get('address', None)
  locality = location.get('locality', None)
  region = location.get('region', None)
  postal_code = location['postal_code']
  country = location['country']

  lat, lon = geocodeLocation(postal_code, country, address, locality, region)
  playerLocation, created = PlayerLocation.objects.get_or_create(
      player=player,
      defaults={
        'point' : Point(lon, lat),
        'address' : address,
        'locality' : locality,
        'region' :  region,
        'postal_code' : postal_code,
        'country' : country
      }
    )

  if not created:
    playerLocation.point = Point(lon, lat)
    playerLocation.address = address
    playerLocation.locality = locality
    playerLocation.region = region
    playerLocation.postal_code = postal_code
    playerLocation.country = country
    playerLocation.save()


class HttpJSONResponse(HttpResponse):

  def __init__(self, content, status=200):
    super(HttpJSONResponse, self).__init__(content, status=status, content_type="text/json; charset=utf-8")
