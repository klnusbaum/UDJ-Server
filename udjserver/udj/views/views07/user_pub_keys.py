import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from udj.headers import MISSING_RESOURCE_HEADER

from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.responses import HttpMissingResponse, HttpJSONResponse
from udj.models import UserPubKey
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.auth import getUserForTicket

@NeedsAuth
@AcceptsMethods(['GET'])
def getUserPubKey(request, user_id):
  try:
    user = User.objects.get(pk=user_id)
    try:
      pubkey = UserPubKey.objects.get(user=user)
      return HttpJSONResponse(json.dumps(pubkey,cls=UDJEncoder))
    except ObjectDoesNotExist:
      return HttpMissingResponse('public-key')
  except ObjectDoesNotExist:
    return HttpMissingResponse('user')


def getMyPublicKey(user):
  return HttpJSONResponse(json.dumps(UserPubKey.objects.get(user=user), cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET', 'POST', 'DELETE'])
def myPubKeyOps(request):
  user = getUserForTicket(request)
  if request.method == 'GET':
    return getMyPublicKey(user)
