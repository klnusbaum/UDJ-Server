from httplib import HTTPSConnection
from udj.exceptions import LocationNotFoundError
from urllib import urlencode

def USCWebGISGeocoder(location, apiKey):
  uscwebgisUrl = "/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V02_96.aspx?"
  #TODO Need to scrub location values. could be vulnerable to a url redirect
  queryParams = dict(location.items())
  del queryParams['address']
  queryParams['streetAddress'] = location['address']
  queryParams['apiKey'] = apiKey
  queryParams['version'] = '2.96'
  queryParams['format'] = 'csv'
  requestUrl = uscwebgisUrl + urlencode(queryParams)

  conn = HTTPSConnection('webgis.usc.edu')
  geocodeRequest = conn.request('GET', requestUrl)
  response = conn.getresponse()
  if response.status != 200:
    print
    print response.read()
    raise LocationNotFoundError('Status code was not 200')

  parsedData = response.read().split(',')
  if parsedData[2] != "200":
    raise LocationNotFoundError('results contained error')

  return (parsedData[3] , parsedData[4])
