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
import MahData
import json
import web
import AuthMethods
from PartyMethods import Party

def addClientIds(parray, serverClientMap):
  toReturn = parray
  for item in toReturn:
    if item.getServerId() in serverClientMap:
      item.setClientId( serverClientMap[item.getServerId()])
  return toReturn

def processNewlyAdded(added, db):
  serverClientMap = dict()
  for newSong in added:
    newServerId = db.insert('mainplaylist', libraryId=newSong['server_lib_id'])
    serverClientMap[newServerId] = newSong['client_playlist_id']
  return serverClientMap
  

def processVotedUp(votedUp, db):
  #TODO Finsish this methdo
  print 'Finish voting up processing'

def processVotedDown(votedDown, db):
  #TODO Finsish this methdo
  print 'Finish voting down processing'

def processSyncInfo(syncinfo, db):
  print syncinfo.keys()
  serverClientMap = processNewlyAdded(syncinfo['added'], db)
  processVotedUp(syncinfo['votedUp'], db)
  processVotedDown(syncinfo['votedDown'], db)
  return serverClientMap


def getObject(dbrow):
  isDel = False
  if(dbrow.isDeleted):
    isDel = true
  return PlaylistEntry(
    dbrow.plId,
    dbrow.priority,
    dbrow.libraryId,
    dbrow.song,
    dbrow.artist,
    dbrow.album,
    dbrow.voteCount,
    dbrow.timeAdded,
    isDel)
    
def getArrayFromResults(results):
  toReturn = []
  for result in results:
    toReturn.append(getObject(result))
  return toReturn


class PlaylistEntry:
  INVALID_SERVER_ID = -1
  INVALID_LIB_ID = -1
  INVALID_CLIENT_ID = -1
  DEFAULT_VOTE_NUM = 1
  INVALID_TIME_ADDED = 'unknown'
  IS_DELETED_DEFAULT=False
  INVALID_PRIORITY = -1

  SERVER_ID_PARAM = 'server_playlist_id'
  PRIORITY_PARAM = 'priority'
  LIBRARY_ID_PARAM = 'server_lib_id'
  SONG_PARAM = 'song'
  ARTIST_PARAM = 'artist'
  ALBUM_PARAM = 'album'
  VOTES_PARAM = 'votes'
  TIME_ADDED_PARAM = 'time_added'
  IS_DELETED_PARAM = 'is_deleted'
  CLIENT_ID_PARAM = 'client_playlist_id'

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
    isDeleted=IS_DELETED_DEFAULT,
    clientId=INVALID_CLIENT_ID
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
    self._clientId = clientId

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

  def setClientId(self, clientId):
    self._clientId = clientId

  def getClientId(self):
    return self._clientId
    
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
        PlaylistEntry.IS_DELETED_PARAM : obj.getIsDeleted(),
        PlaylistEntry.CLIENT_ID_PARAM : obj.getClientId()
      }
    else:
      return json.JSONEncoder.default(self, obj)

class Playlist:
  def GET(self):
    if( 
      web.ctx.session.loggedIn == 1 and
      web.ctx.session.loggedIn != Party.INVALID_PARTY_ID
    ):
      data = web.input()
      db = MahData.getDBConnection()
      results = db.select('main_playlist_view')
      parray = getArrayFromResults(results)
      web.header('Content-Type', 'application/json')
      return json.dumps(parray, cls=PlaylistJSONEncoder)
    else:
      Auth.doUnAuth('Getting playlist')
  def POST(self):
    if( 
      web.ctx.session.loggedIn == 1 and
      web.ctx.session.loggedIn != Party.INVALID_PARTY_ID
    ):
      db = MahData.getDBConnection()
      jsonSyncInfo = json.loads(web.input().syncinfo)
      serverClientMap = processSyncInfo(jsonSyncInfo, db)
      results = db.select('main_playlist_view')
      parray = getArrayFromResults(results)
      parray = addClientIds(parray, jsonSyncInfo['added'])
      web.header('Content-Type', 'application/json')
      return json.dumps(parray, cls=PlaylistJSONEncoder)
    else:
      Auth.doUnAuth('Syncing playlist')

class VoteUpSongs:
  def POST(self):
    #TODO actually impelment this
    return None
  
class VoteDownSongs:
  def POST(self):
    #TODO actually impelment this
    return None
