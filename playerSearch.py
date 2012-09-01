from httplib import HTTPConnection
from urllib import urlencode
from udjTestCaller import getAuthToken
import json

ticket, userId = getAuthToken('kurtis', 'testkurtis')
requestUrl = "/udj/0_6/players?name=test"
conn = HTTPConnection('localhost:8000')
authRequest = conn.request('GET', requestUrl, headers={'X-Udj-Ticket-Hash': ticket})
response = conn.getresponse()
data = response.read()
print data
