"""
Copyright 2011 Kurtis L. Nusbaum

This file is part of UDJ.

UDJ is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

UDJ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
"""
import web

class Authenticator:
  USERNAME_PARAM = 'username'
  PASSWORD_PARAM = 'password'
  def POST(self):
    data = web.input()
    if(Authenticator.isUserValid(data.username, data.password)):
      #TODO need to set domain to www.bazaarsolutions.com
      web.setcookie('LOGGED_IN', True, 43200)
      web.setcookie('USERNAME', data.username)
      web.setcookie('AUTH_HASH', Authenticator.getAuthHash(data.password))
    else:
      return None

  @staticmethod
  def getAuthHash(username):
    #TODO actually implement this
    return 'blahblahblah'

  @staticmethod
  def isUserValid(username, password):
    #TODO actually implement this
    return True

  @staticmethod
  def isAuthenticated(cookies):
    logged_in = False
    authhash = None
    username = ''
    try:
      logged_in = cookies.LOGGED_IN
      userhash = cookies.AUTH_HASH
      username = cookies.USERNAME
    except:
      return False
    return (logged_in and
      Authenticator.usernameMatchesHash(username, userhash))

  @staticmethod
  def usernameMatchesHash(username, userhash):
    #TODO actually implement this
    return True


