import json

from udj.models import SortingAlgorithm
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.views.views07.responses import HttpJSONResponse

@NeedsAuth
@AcceptsMethods(['GET'])
def getSortingAlgorithms(request):
  allAlgos = SortingAlgorithm.objects.all()
  return HttpJSONResponse(json.dumps(allAlgos, cls=UDJEncoder))
