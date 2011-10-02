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
import json
import web
import AuthMethods
from AuthMethods import Authenticator

class Party:
  INVALID_PARTY_ID = -1
  ID_PARAM = 'id'
  NAME_PARAM = 'name'

  def __init__(self, id=INVALID_PARTY_ID, name=''):
    self._id = id
    self._name = name

  def getId(self):
    return self._id

  def getName(self):
    return self._name

class PartyJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Party):
      return {Party.ID_PARAM : obj.getId(), Party.NAME_PARAM : obj.getName()}
    else:
      return json.JSONEncoder.default(self, obj)
  
class PartyLocator:
  def GET(self):
    if( web.ctx.session.loggedIn == 1 ):
      p1 = Party('1', 'Steve Party')
      p2 = Party('2', 'Kurtis Party')
      parray = list()
      parray.append(p1)
      parray.append(p2)
      web.header('Content-Type', 'application/json')
      return json.dumps(parray, cls=PartyJSONEncoder)
    else:
      AuthMethods.doUnAuth('Getting parties')
      return None

class PartyLogin:
  def POST(self):
    if(web.ctx.session.loggedIn == 1):
      data = web.input()
      #TODO actuall log them into the party
      web.ctx.session.partyId = data.partyId
      web.setcookie('partyId', data.partyId)
    else:
      return Auth.doUnAuth('Party Login')

class PartyUsers:
  def GET(self):
    #TODO implement this method
    return None

class KickUsers:
  def POST(self):
    #TODO IMPLEMENT THIS METHOD
    return None

