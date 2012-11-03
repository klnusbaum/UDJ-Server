import oauth2 as oauth
import urllib
from settings import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET
import json

consumer = oauth.Consumer(RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET)
client = oauth.Client(consumer)


def convertToUDJLibEntries(results):
  return [
      {
        'id' : "rdio://%s" % x['key'],
        'title' : x['name'],
        'artist' : x['artist'],
        'album' : x['album'],
        'track' : x['trackNum'],
        'genre' : '',
        'duration' : x['length']
      }
      for x in results
  ]

def search(query):
  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'search', 'query': query, 'types' : 'Track'}))
  responseJSON = json.loads(response[1])
  return convertToUDJLibEntries(responseJSON['result']['results'])

def artists():
  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'getHeavyRotation', 'type': 'artists', 'count' : 1000}))
  responseJSON = json.loads(response[1])
  return [x['name'] for x in responseJSON['result']]

def getSongsForArtist(artist):
  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method' : 'search', 'query': artist, 'types': 'artist' }))
  responseJSON = json.loads(response[1])
  if len(responseJSON['result']['results']) < 1:
    return []

  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method' : 'getTracksForArtist', 'artist': responseJSON['result']['results'][0]['key']}))
  trackJSON = json.loads(response[1])['result']
  return convertToUDJLibEntries(trackJSON)
