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
import Auth
from Parties import Party

class PlaylistEntry:
  INVALID_SERVER_ID = -1
  INVALID_LIB_ID = -1
  DEFAULT_VOTE_NUM = 1
  INVALID_TIME_ADDED = 'unknown'
  SERVER_ID_PARAM = 'server_id'
  VOTES_PARAM = 'votes'
  LIBRARY_ID_PARAM = 'libid'
  TIME_ADDED_PARAM = 'time_added'

  def __init__(self, server_id=INVALID_SERVER_ID, votes=DEFAULT_VOTE_NUM, libid=INVALID_LIB_ID, timeAdded=INVALID_TIME_ADDED):
    self._serverId = server_id
    self._votes = votes
    self._libid = libid
    self._timeAdded = timeAdded

  def getServerId(self):
    return self._serverId

  def getVotes(self):
    return self._votes

  def getLibId(self):
    return self._libid

  def getTimeAdded(self):
    return self._timeAdded
    
class PlaylistJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, PlaylistEntry):
      return {
        PlaylistEntry.SERVER_ID_PARAM : obj.getServerId(),
        PlaylistEntry.VOTES_PARAM : obj.getVotes(),
        PlaylistEntry.LIBRARY_ID_PARAM : obj.getLibId(),
        PlaylistEntry.TIME_ADDED_PARAM : obj.getTimeAdded()
      }
    else:
      return json.JSONEncoder.default(self, obj)

class RESTPlaylist:
  def GET(self):
    if( web.ctx.session.loggedIn == 1 or 
      web.ctx.session.loggedIn != Party.INVALID_PARTY_ID):
      p1 = PlaylistEntry(1, 4, 1, '2011-08-27 22:40:30')
      p2 = PlaylistEntry(2, 3, 4, '2011-08-27 22:39:30')
      parray = list()
      parray.append(p1)
      parray.append(p2)
      web.header('Content-Type', 'application/json')
      return json.dumps(parray, cls=PlaylistJSONEncoder)
    else:
      Auth.doUnAuth()
  
