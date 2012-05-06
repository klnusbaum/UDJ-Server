from httplib import HTTPSConnection
from urllib import urlencode
import json

def getAuthToken(username, password):
  requestUrl = "/udj/auth"
  conn = HTTPSConnection('www.udjplayer.com:4898')
  params = urlencode({'username' : username, 'password' : password})
  authRequest = conn.request('POST', requestUrl, params)
  response = conn.getresponse()
  data = response.read()
  response = json.loads(data)
  return (response["ticket_hash"], response["user_id"])
