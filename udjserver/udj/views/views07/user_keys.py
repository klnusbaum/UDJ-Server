from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from udj.headers import MISSING_RESOURCE_HEADER

from udj.views.views07.decorators import AcceptsMethods
from udj.views.views06.responses import HttpMissingResponse
from udj.models import UserPubKey

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
    return HttpMissingResponse('song')

