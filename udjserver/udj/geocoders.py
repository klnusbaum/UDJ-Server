def USCWebGISGeocoder(location, apiKey):
  uscwebgisUrl = \
  "https://webgis.usc.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V02_96.aspx"
  #TODO Need to scrub location values. could be vulnerable to a url redirect
  requestUrl = uscwebgisUrl + "?apiKey=" + GEOCODER_API_KEY + "version=2.96&" +\
      "streetAddress=" + location['address'] + "&state=" + location['state'] +\
      "&city=" + location['city'] + "&zipcode=" + location['zipcode'] +\
      "&format=csv"

  geocodeRequest = HTTPConnection.request('GET', requestUrl)
  response = geocodeRequest.getresponse().read().split(',')
  if response[2] != "200":
    raise LocationNotFoundError

  return (response[3] , resposne[4])
