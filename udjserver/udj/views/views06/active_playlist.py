import json

from udj.models import Participant, Player

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed

from udj.views.views06.decorators import PlayerExists, PlayerIsActive, AcceptsMethods, UpdatePlayerActivity, HasNZParams
from udj.views.views06.authdecorators import NeedsAuth, IsOwnerOrParticipates
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@AcceptsMethods(['GET', 'POST'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@UpdatePlayerActivity
@transaction.commit_on_success
def activePlaylist(request, player_id, player):
  if request.method == 'GET':
    return getActivePlaylist(player)
  elif request.method == 'POST':
    return multiModActivePlaylist(request, player)
  else:
    #Should never get here because of the AcceptsMethods decorator
    #Put here because I'm pedantic sometimes :/
    return HttpResponseNotAllowed(['POST', 'DELETE'])

def getActivePlaylist(player)
  return HttpJSONResponse(json.dumps(player.ActivePlaylist(), cls=UDJEncoder))

@HasNZParams(['to_add','to_remove'])
def multiModeActivePlaylist(request, player):
  pass
