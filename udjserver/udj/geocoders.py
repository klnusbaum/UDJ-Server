from httplib import HTTPSConnection, HTTPConnection
from udj.exceptions import LocationNotFoundError
from urllib import urlencode
import json

def USCWebGISGeocoder(address, locality, region, zipcode, apiKey):
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



def yahooGeocoder(address, locality, region, postalcode, appId):
  yahooUrl = "/geocode?"
  queryParams = {
      'q' : address + ' ' + locality +' ' + region + ' ' + str(postalcode),
      'appid' : appId,
      'flags' : 'J'
  }
  requestUrl = yahooUrl + urlencode(queryParams)
  conn = HTTPConnection('where.yahooapis.com')
  geocodeRequest = conn.request('GET', requestUrl)
  response = conn.getresponse()
  if response.status != 200:
    raise LocationNotFoundError('Status code was not 200')

  responseString = response.read()
  resultSet = json.loads(responseString)['ResultSet']
  results = resultSet['Results']
  return (float(results[0]['latitude']), float(results[0]['longitude']))


