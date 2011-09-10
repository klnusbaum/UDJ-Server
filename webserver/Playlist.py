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
  IS_DELETED_DEFAULT=False
  INVALID_PRIORITY = -1

  SERVER_ID_PARAM = 'server_id'
  PRIORITY_PARAM = 'priority'
  LIBRARY_ID_PARAM = 'lib_id'
  SONG_PARAM = 'song'
  ARTIST_PARAM = 'artist'
  ALBUM_PARAM = 'album'
  VOTES_PARAM = 'votes'
  TIME_ADDED_PARAM = 'time_added'
  IS_DELETED_PARAM = 'is_deleted'

  def __init__(
    self, 
    server_id=INVALID_SERVER_ID,
    priority=INVALID_PRIORITY,
    libid=INVALID_LIB_ID, 
    song='unknown',
    artist='unknown',
    album='unknown',
    votes=DEFAULT_VOTE_NUM, 
    timeAdded=INVALID_TIME_ADDED,
    isDeleted=IS_DELETED_DEFAULT
  ):
    self._serverId = server_id
    self._priority = priority
    self._libid = libid
    self._song = song
    self._artist = artist
    self._album = album
    self._votes = votes
    self._timeAdded = timeAdded
    self._isDeleted = isDeleted

  def getServerId(self):
    return self._serverId

  def getPriority(self):
    return self._priority

  def getLibId(self):
    return self._libid

  def getSong(self):
    return self._song

  def getSong(self):
    return self._song

  def getArtist(self):
    return self._artist

  def getAlbum(self):
    return self._album

  def getVotes(self):
    return self._votes

  def getTimeAdded(self):
    return self._timeAdded

  def getIsDeleted(self):
    return self._isDeleted
    
class PlaylistJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, PlaylistEntry):
      return {
        PlaylistEntry.SERVER_ID_PARAM : obj.getServerId(),
        PlaylistEntry.PRIORITY_PARAM : obj.getPriority(),
        PlaylistEntry.LIBRARY_ID_PARAM : obj.getLibId(),
        PlaylistEntry.SONG_PARAM : obj.getSong(),
        PlaylistEntry.ARTIST_PARAM : obj.getArtist(),
        PlaylistEntry.ALBUM_PARAM : obj.getAlbum(),
        PlaylistEntry.VOTES_PARAM : obj.getVotes(),
        PlaylistEntry.TIME_ADDED_PARAM : obj.getTimeAdded(),
        PlaylistEntry.IS_DELETED_PARAM : obj.getIsDeleted()
      }
    else:
      return json.JSONEncoder.default(self, obj)

class RESTPlaylist:
  def GET(self):
    if( 
      web.ctx.session.loggedIn == 1 and
      web.ctx.session.loggedIn != Party.INVALID_PARTY_ID
    ):
      p1 = PlaylistEntry(1, 2, 1,  'Hello', 'Steve', 'Blue Harvest', 1, 
        '2011-08-27 22:40:30', False)
      p2 = PlaylistEntry(2, 4, 2,  'Bark', 'Steve', 'Blue Harvest', 1, 
        '2011-08-27 23:40:30', False)
      parray = list()
      parray.append(p1)
      parray.append(p2)
      web.header('Content-Type', 'application/json')
      return json.dumps(parray, cls=PlaylistJSONEncoder)
    else:
      Auth.doUnAuth('Getting playlist')
  
