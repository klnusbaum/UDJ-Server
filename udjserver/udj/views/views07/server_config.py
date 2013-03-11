import json

from udj.models import SortingAlgorithm
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.views.views07.responses import HttpJSONResponse
from settings import MIN_SEARCH_RADIUS, MAX_SEARCH_RADIUS

@NeedsAuth
@AcceptsMethods(['GET'])
def getSortingAlgorithms(request):
  allAlgos = SortingAlgorithm.objects.all()
  return HttpJSONResponse(json.dumps(allAlgos, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET'])
def getAcceptableSearchRadii(request):
  return HttpJSONResponse(json.dumps({
                                       'min_radius' : MIN_SEARCH_RADIUS,
                                       'max_radius' : MAX_SEARCH_RADIUS
                                      }
                                    ))
