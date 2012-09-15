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
from django.db import transaction

@csrf_exempt
@AcceptsMethods['PUT']
@NeedsAuth
@PlayerExists
@CanCreatSongSets
@NeedsJSON
@transaction.commit_on_success
def createSongSet(request, player_id, player):
  user = getUserForTicket(request)

  try:
    songSetJSON = json.loads(request.raw_post_data)
    if 'name' not in songSetJSON or 'description' not in songSetJSON or 'date_created' not in songSetJSON:
      return HttpResponseBadRequest('Bad JSON')
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  if player.Songsets().filter(name=songSetJSON['name']).exclude(description=songSetJSON['description'], date_created=songSetJSON['date_created']).exists():
    return HttpResponse('duplicate song set', status=409)


  newSongSet = SongSet(player, songSetJSON['name'], ['desciption'], user, songSetJSON['date_created'])

  newSongSet.save()
  return HttpResonse(status=201)


