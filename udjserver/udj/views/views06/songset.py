import json

from udj.headers import MISSING_RESOURCE_HEADER
from udj.models import Player
from udj.models import SongSet
from udj.models import SongSetEntry
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import PlayerExists
from udj.views.views06.decorators import HasNZParams
from udj.views.views06.authdecorators import IsOwnerOrAdmin
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.auth import getUserForTicket

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@AcceptsMethods['PUT']
@NeedsAuth
@PlayerExists
@CanCreatSongSets
@NeedsJSON
def createSongSet(request, player_id, player):
  user = getUserForTicket(request)

  try:
    songSetJSON = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  if 
