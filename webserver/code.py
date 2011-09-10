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
from Parties import Party
from Parties import RESTParty
from Playlist import RESTPlaylist
from Library import RESTLibrary
from Auth import Authenticator
from Parties import PartyLogin

web.config.debug = False

urls = (
"/parties", "RESTParty",
"/playlist", "RESTPlaylist",
"/library", "RESTLibrary",
"/auth", "Authenticator" ,
"/party_login", "PartyLogin"
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), 
  initializer={'loggedIn' : 0, 'partyId' : Party.INVALID_PARTY_ID})

def session_hook():
  web.ctx.session = session

app.add_processor(web.loadhook(session_hook))



if __name__ == "__main__": 
  app.run()

