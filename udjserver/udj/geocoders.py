from httplib import HTTPSConnection
from udj.exceptions import LocationNotFoundError
from urllib import urlencode

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
    print
    print response.read()
    raise LocationNotFoundError('Status code was not 200')

  parsedData = response.read().split(',')
  if parsedData[2] != "200":
    raise LocationNotFoundError('results contained error')

  return (float(parsedData[3]) , float(parsedData[4]))
