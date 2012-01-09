from udj.models import *
from django.contrib import admin

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'event', 'state')
  list_filter = ('state','event',)

class EventGoerAdmin(admin.ModelAdmin):
  list_display = ('user', 'event', 'time_joined', 'state')
  list_filter = ('event', 'state')

admin.site.register(Ticket)
admin.site.register(Event)
admin.site.register(EventEndTime)
admin.site.register(EventPassword)
admin.site.register(EventLocation)
admin.site.register(LibraryEntry)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(EventGoer, EventGoerAdmin)
admin.site.register(AvailableSong)
admin.site.register(Vote)
admin.site.register(PlaylistEntryTimePlayed)
