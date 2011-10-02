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
import json
import MahData
from PartyMethods import Party


from AuthMethods import Authenticator
from PartyMethods import PartyLocator
from PartyMethods import PartyLogin
from PartyMethods import PartyUsers
from PartyMethods import KickUsers
from PlaylistMethods import Playlist
from PlaylistMethods import VoteUpSongs
from PlaylistMethods import VoteDownSongs
from LibraryMethods import LibrarySearch
from LibraryMethods import LibraryRandom
from LibraryMethods import Library


web.config.debug = False

def session_hook():
  web.ctx.session = session

def initDatabase(db):
  db.query("DROP VIEW IF EXISTS main_playlist_view;")
  db.query("DROP TABLE IF EXISTS mainplaylist;")
  db.query("DROP TABLE IF EXISTS library;")
  db.query("CREATE TABLE IF NOT EXISTS library "
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "hostId INTEGER, "
 	  "song TEXT NOT NULL, artist TEXT, album TEXT, "
    "isDeleted BIT(0) DEFAULT '0');")
  db.query("CREATE TABLE IF NOT EXISTS mainplaylist "
 	  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
 	  "libraryId INTEGER REFERENCES library (id) ON DELETE CASCADE, "
 	  "voteCount INTEGER DEFAULT 1, "
    "priority INTEGER DEFAULT 1, "
 	  "timeAdded TEXT DEFAULT CURRENT_TIMESTAMP, "
    "isDeleted BIT(0) DEFAULT '0');")
  db.query("CREATE VIEW IF NOT EXISTS main_playlist_view "
    "AS SELECT "
    "mainplaylist.id AS plId, "
    "mainplaylist.libraryId AS libraryId, "
    "library.song AS song, "
    "library.artist AS artist, "
    "library.album AS album, "
    "mainplaylist.voteCount AS voteCount, "
    "mainplaylist.priority AS priority, "
    "mainplaylist.timeAdded AS timeAdded, "
    "mainplaylist.isDeleted AS isDeleted "
    "FROM mainplaylist INNER JOIN library ON "
    "mainplaylist.libraryId = library.id ORDER BY priority DESC;")


urls = (
"/auth", "Authenticator",
"/party/parties", "PartyLocator",
"/party/party_login", "PartyLogin",
"/party/party_users", "PartyUsers",
"/party/kick_user", "KickUser",
"/playlist", "Playlist",
"/playlist/vote_up_songs", "VoteUpSongs",
"/playlist/vote_down_songs", "VoteDownSongs",
"/library/search_library", "LibrarySearch",
"/library/random", "LibraryRandom",
"/library", "Library"
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), 
  initializer={'loggedIn' : 0, 'partyId' : Party.INVALID_PARTY_ID})
db = MahData.getDBConnection()
initDatabase(db)

app.add_processor(web.loadhook(session_hook))


if __name__ == "__main__": 
  app.run()

