import oauth2 as oauth
import urllib
from settings import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET
import json
from udj.models import LibraryEntry
from django.db.models import Q
from datetime import datetime

last_rdio_heavy_rotation_query = None
consumer = oauth.Consumer(RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET)
client = oauth.Client(consumer)

def do_rdio_query(params):
  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(params))
  return json.loads(response[1])

def insert_songs_into_rdio_library(songJSON, library):
  for song in songJSON:
    #if lib_ids ever become non-unique (i.e. are recycled) this will most likely blow up on some
    #corner case and thus piss me the fuck off. Don't do it Rdio. Just don't do it.
    #Otherwise I'll get mad at you.
    LibraryEntry.objects.get_or_create(library=library,
                                       lib_id=song['key'],
                                       title=song['name'],
                                       artist=song['artist'],
                                       album=song['album'],
                                       track=song['trackNum'],
                                       genre='',
                                       duration=song['duration'])


def search(query, library, player):
  params = {'method': 'search', 'query': query, 'types' : 'Track'}
  response = do_rdio_query(params)
  #print "\nrdio search reasponse"
  #print response['result']['results']
  insert_songs_into_rdio_library(response['result']['results'], library)
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .filter(Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
                              .exclude(is_deleted=True)
                              .exclude(id__in=bannedIds))


def artists(library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True)
                              .distinct('artist')
                              .order_by('artist')
                              .values_list('artist', flat=True))

def getSongsForArtist(artist, library, player):

  #first get artist key. We'll just assume the top artist returned is the best match
  #for now
  params = {'method': 'search', 'query': artist, 'types' : 'Artist'}
  response = do_rdio_query(params)
  if len(response['result']['results']) < 1:
    return EmptyQuery()
  artist_key = response['result']['results'][0]['key']

  #Get all the songs for the artist we found above
  params = {'method': 'getTracksForArtist', 'artist': artist_key}
  response = do_rdio_query(params)
  #print "Rdio response {0}".format(json.dumps(response, indent=2))
  insert_songs_into_rdio_library(response['result'], library)
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library, artist__iexact=artist)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True))

"""
def load_up_heavy_rotation(library):
  params = {'method': 'getHeavyRotation', 'type': 'artists', 'count' : 100}
  artist_keys = [artist['key'] for artist in do_rdio_query(params)['result']]
"""

def randoms(library, player):
  #So at first this might not return much. But as we populate our library, I think things
  #will be fine
  #that said, I still wanna figure out how to mixin some heavy rotation artists
  """
  if (last_rdio_heavy_rotation_query == None or
      (datetime.now - last_rdio_heavy_rotation_query).days > 0):
    load_up_heavy_rotation(library)
  """
  return (LibraryEntry.objects.filter(library=library)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True)
                              .order_by('?'))

