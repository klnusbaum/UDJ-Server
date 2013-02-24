import json

from udj.models import SortingAlgorithm
from udj.views.views06.decorators import AcceptsMethods
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.JSONCodecs import UDJEncoder
from udj.views.views06.helpers import HttpJSONResponse

from django.http import HttpRequest
from django.http import HttpResponse

@NeedsAuth
@AcceptsMethods(['GET'])
def getSortingAlgorithms(request):
  allAlgos = SortingAlgorithm.objects.all()
  return HttpJSONResponse(json.dumps(allAlgos, cls=UDJEncoder))
