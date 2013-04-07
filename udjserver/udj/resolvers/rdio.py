import oauth2 as oauth
import urllib
from settings import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET
import json


consumer = oauth.Consumer(RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET)
client = oauth.Client(consumer)

def do_rdio_query(params):
  response = client.reqeust('http://api.rdio.com/1/', 'POST', urllib.urlencode(params))
  return json.loads(response[1])

def insert_songs_into_rdio_libaray(songsJSON, library):
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
                                       duration=song['length'])


def search(query, library, player):
  params = {'method': 'search', 'query': query, 'types' : 'Track'}
  response = do_rdio_query(param)
  insert_songs_into_rdio_library(['result']['results'], library)
  return (LibraryEntry.objects.filter(library=library)
                              .filter(Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
                              .exclude(is_deleted=True)
                              .exclude(id__in=bannedIds))


def artists(library, player):
  params = {'method': 'getHeavyRotation',
            'type': 'artists',
            'count' : 1000}
  response = do_rdio_query(params)
  return [x['name'] for x in responseJSON['result']]

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
  insert_songs_into_rdio_library(['result']['results'], library)
  return (LibraryEntry.objects.filter(library=library, artist__iexact=artist)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True))

