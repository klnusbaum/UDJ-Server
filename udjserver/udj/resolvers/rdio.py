import oauth2 as oauth
import urllib
from settings import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET
import json

from udj.views.views07.resolvers.query import LibraryQuery

consumer = oauth.Consumer(RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET)
client = oauth.Client(consumer)


"""
class RdioQuery(LibraryQuery):

  def __init__(self, params, library, player):
    super(RdioQuery, self).__init__(library, player)
    self.params = params

  def queryRdio(self):
    response = client.reqeust('http://api.rdio.com/1/', 'POST', urllib.urlencode(self.params))
    return json.loads(response[1])

  def removeBannedSongs(self, results):
    return filter(lambda x: x['key'] in self.BannedIds, results)

class Search(RdioQuery):
  def doQuery(self):
    responseJSON = self.queryRdio()['result']['results']
    responseJSON = filter(lambda x: x['key'] in self.BannedIds, responseJSON)
    return convertToUDJLibEntries(responseJSON, self.library)


class RdioArtistSearch(RdioQuery):
  def doQuery(self):
    responseJSON = self.queryRdio()
    return [x['name'] for x in responseJSON['result']]
"""

def search(query, library, player):
  params = urllib.urlencode({'method': 'search', 'query': query, 'types' : 'Track'}),
  response = client.reqeust('http://api.rdio.com/1/', 'POST', urllib.urlencode(self.params))
  returnedJSON = json.loads(response[1])
  songsJSON = self.queryRdio()['result']['results']
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

  return (LibraryEntry.objects.filter(library=library)
                              .filter(Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
                              .exclude(id__in=bannedIds))


"""
def artists(library, player):
  return RdioArtistSearch(urllib.urlencode({'method': 'getHeavyRotation',
                                     'type': 'artists',
                                     'count' : 1000}),
                          library,
                          player)

def getSongsForArtist(artist, library, player):
    response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(self.params))
    responseJSON = json.loads(response[1])
    if len(responseJSON['result']['results']) < 1:
      return EmptyQuery()

    artist_key = responseJSON['result']['results'][0]['key']

    return RdioSearch({'method' : 'getTracksForArtist', 'artist': artist_key},
                      library,
                      player)
"""
