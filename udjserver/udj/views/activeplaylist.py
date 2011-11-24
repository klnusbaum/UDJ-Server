from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from udj.decorators import AcceptsMethods
from udj.decorators import NeedsJSON
from udj.decorators import NeedsAuth
from udj.decorators import InParty
from udj.models import ActivePlaylistEntry
from udj.JSONCodecs import getJSONForActivePlaylistEntries

@NeedsAuth
@InParty
@AcceptsMethods('GET')
def getActivePlaylist(request, event_id):
  """
  My guess is that if you help write the software for DMBSes, this query is
  going to make your cry. My sincerest apologies
  """
  playlistEntries = ActivePlaylistEntry.objects.filter(event__id=event_id).\
    extra(
      select={
        'upvotes' : 'SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.id',

        'downvotes' : 'select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.id',
        'total_votes' : '(SELECT COUNT(*) FROM udj_upvote where ' +\
        'udj_upvote.playlist_entry_id = udj_activeplaylistentry.id)-' +\
        '(select count(*) from udj_downvote where ' +\
        'udj_downvote.playlist_entry_id = udj_activeplaylistentry.id)'
      },
      order_by = ['-total_votes', 'time_added'])
    
  return HttpResponse(getJSONForActivePlaylistEntries(playlistEntries))
