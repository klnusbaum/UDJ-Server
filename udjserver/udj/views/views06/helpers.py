from udj.models import Player
from udj.models import PlayerLocation
from settings import geocodeLocation

from django.contrib.gis.geos import Point

def isValidLocation(location):
  return 'postal_code' in location and 'country' in location



def setPlayerLocation(location, player):
  lat, lon = geocodeLocation(location['postal_code'], location['country'], location.get('address', None), location.get('locality', None), location.get('region', None))
  playerLocation, created = PlayerLocation.objects.get_or_create(
      player=player,
      defaults={
        'point' : Point(lon, lat)
      }
    )

  if not created:
    playerLocation.point = Point(lon, lat)
    playerLocation.save()

