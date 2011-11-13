from udj.models import Ticket
from udj.models import Event
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import EventGoer
from udj.models import Playlist
from udj.models import PlaylistEntry
from django.contrib import admin

admin.site.register(Ticket)
admin.site.register(Event)
admin.site.register(LibraryEntry)
admin.site.register(ActivePlaylistEntry)
admin.site.register(EventGoer)
admin.site.register(Playlist)
admin.site.register(PlaylistEntry)
