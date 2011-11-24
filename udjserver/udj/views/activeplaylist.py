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
  playlistEntries = ActivePlaylistEntry.objects.filter(event__id=event_id).\
    extra(
      select={'total_votes' : 'select count(*) from udj_upvote where playlist_entry_id = udj_activeplaylistentry.id - select count(*) from udj_downvote where playlist_entry_id = udj_activeplaylistentry.id'},
      order_by = ['-total_votes', 'time_added'])
    
  return HttpResponse(
    getJSONForActivePlaylistEntries(playlistEntries)
  )
