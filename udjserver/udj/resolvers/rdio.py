import oauth2 as oauth
import urllib
from settings import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET
import json

from udj.resolvers.query import LibraryQuery

consumer = oauth.Consumer(RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET)
client = oauth.Client(consumer)


class RdioQuery(LibraryQuery):

  def __init__(self, params, library, player):
    super(RdioQuery, self).__init__(library, player)
    self.params = params

  def __getitem__(self, key):
    if isinstance(key, slice):
      if key.start is not None
        self.params['start'] = int(key.start)
      if key.stop is not None:
        if self.start is not None:
          self.params['count'] = key.stop - key.start
        else:
          self.params['count'] = key.stop
      return self
    else:
      raise TypeError

  def convertToUDJLibEntries(results):
    return [
        {
          'id' : "{0}".format(x['key']),
          'library_id' : '{0}'.format(self.library.id),
          'title' : x['name'],
          'artist' : x['artist'],
          'album' : x['album'],
          'track' : x['trackNum'],
          'genre' : '',
          'duration' : x['length']
        }
        for x in results
    ]

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









def search(query, library, player):
  return RdioSearch(urllib.urlencode({'method': 'search', 'query': query, 'types' : 'Track'}),
                   library,
                   player)

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
