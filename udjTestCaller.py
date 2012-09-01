from httplib import HTTPConnection
from urllib import urlencode
import json

def getAuthToken(username, password):
  requestUrl = "/udj/0_6/auth"
  conn = HTTPConnection('localhost:8000')
  params = urlencode({'username' : username, 'password' : password})
  authRequest = conn.request('POST', requestUrl, params)
  response = conn.getresponse()
  data = response.read()
  response = json.loads(data)
  return (response["ticket_hash"], response["user_id"])
