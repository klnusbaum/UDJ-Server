from httplib import HTTPSConnection
from urllib import urlencode

requestUrl = "/udj/auth"
conn = HTTPSConnection('www.udjplayer.com:4898')
params = urlencode({'username' : 'test5', 'password' : 'fivetest'})
authRequest = conn.request('POST', requestUrl, params)
response = conn.getresponse()
data = response.read()
print data
