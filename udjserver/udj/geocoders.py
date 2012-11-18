from udj.exceptions import LocationNotFoundError
from urllib import urlencode
import json
import oauth2 as oauth
import time



def USCWebGISGeocoder(address, locality, region, zipcode, apiKey):
  from httplib import HTTPSConnection
  """
  Note this geocoder no longer works as is. It is left here as an example.
  """
  uscwebgisUrl = "/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V02_96.aspx?"
  queryParams = {
    'zip' : zipcode,
    'apiKey' : apiKey,
    'version' : '2.96',
    'format' : 'csv',
  }

  if not address is None:
    queryParams['streetAddress'] = address

  if not locality is None:
    queryParams['city'] = locality

  if not region is None:
    queryParams['state'] = region

  requestUrl = uscwebgisUrl + urlencode(queryParams)


  conn = HTTPSConnection('webgis.usc.edu')
  geocodeRequest = conn.request('GET', requestUrl)
  response = conn.getresponse()
  if response.status != 200:
    raise LocationNotFoundError('Status code was not 200')

  parsedData = response.read().split(',')
  if parsedData[2] != "200":
    raise LocationNotFoundError('results contained error')

  return (float(parsedData[3]) , float(parsedData[4]))



def YahooGeocoder(address, locality, region, postalcode, CONSUMER_KEY, CONSUMER_SECRET):
  import requests
  from requests.auth import OAuth1
  from urllib import quote_plus

  url = u'http://yboss.yahooapis.com/geo/placefinder'
  query_params = {
    'q' : quote_plus(address + ' ' + locality + ' ' + region + ' ' + str(postalcode)),
    'flags' : 'J',
  }


  queryoauth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)
  response = requests.get(url, params=query_params, auth=queryoauth)


  if response.status_code != 200:
    raise LocationNotFoundError('Response status code was not 200')

  try:
    responseJSON = response.json['bossresponse']
  except:
    raise LocationNotFoundError("Didn't get JSON back")

  if responseJSON['responsecode'] != "200":
    raise LocationNotFoundError('Boss Status code was not 200')

  if responseJSON['placefinder']['count'] == 0:
    raise LocationNotFoundError('Location not found')


  result = responseJSON['placefinder']['results'][0]
  return (float(result['latitude']), float(result['longitude']))

