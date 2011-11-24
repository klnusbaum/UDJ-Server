from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import InParty
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from udj.models import ActivePlaylistEntry

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getActivePlaylist(request, event_id):
  playlistEntries = ActivePlaylistEntry.objects.filter(event__id=event_id)
  return HttpResponse(getJSONForActivePlaylistEntries(playlistEntries))
