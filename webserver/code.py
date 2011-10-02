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
from Parties import Party
from Parties import RESTParty
from Playlist import RESTPlaylist
from Library import RESTLibrary
from Auth import Authenticator
from Parties import PartyLogin

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
"/parties", "RESTParty",
"/playlist/get_playlist", "RESTPlaylist",
"/playlist/add_songs", "RESTPlaylist",
"/library/search_library", "RESTLibrary",
"/auth", "Authenticator" ,
"/party/party_login", "PartyLogin",
"/library/add_songs", "RESTLibrary"
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), 
  initializer={'loggedIn' : 0, 'partyId' : Party.INVALID_PARTY_ID})
db = MahData.getDBConnection()
initDatabase(db)

app.add_processor(web.loadhook(session_hook))


if __name__ == "__main__": 
  app.run()

