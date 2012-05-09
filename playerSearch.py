from httplib import HTTPSConnection
from urllib import urlencode
from udjTestCaller import getAuthToken
import json

ticket, userId = getAuthToken('test5', 'fivetest')
requestUrl = "/udj/players?name=test"
conn = HTTPSConnection('www.udjplayer.com:4898')
authRequest = conn.request('GET', requestUrl, headers={'X-Udj-Ticket-Hash': ticket})
response = conn.getresponse()
data = response.read()
print data
