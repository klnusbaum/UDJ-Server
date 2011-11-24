from udj.models import ActivePlaylistEntry
from operator import itemgetter

def sortPlaylist(playlist_entries, upvotes, downvotes):
  entries = playlist_entries.values()
  for entry in entries:
    entry['total_votes'] = \
      upvotes.filter(playlist_entry__id=entry['id']).count() - \
      downvotes.filter(playlist_entry__id=entry['id']).count()
  return sorted(entries, key=lambda k:(-k['total_votes'], k['time_added']))
  
  
  
  

