from udj.models import *
from django.contrib import admin

def removeSongFromActivePlaylist(modeladmin, request, queryset):
  queryset.update(state='RM')

removeSongFromActivePlaylist.short_description = "Remove songs from playlist"

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'event', 'state')
  list_filter = ('state','event',)
  actions = [removeSongFromActivePlaylist]

class EventGoerAdmin(admin.ModelAdmin):
  list_display = ('user', 'event', 'time_joined', 'state')
  list_filter = ('event', 'state')

class LibraryAdmin(admin.ModelAdmin):
  list_display = (
    'host_lib_song_id', 
    'title', 
    'artist', 
    'album', 
    'owning_user', 
    'is_deleted')
  list_filter = ('owning_user', 'is_deleted')

class EventAdmin(admin.ModelAdmin):
  list_display = ('name', 'host', 'time_started', 'state')
  list_filter = ('host', 'state') 

class VoteAdmin(admin.ModelAdmin):
  list_display = ('playlist_entry', 'user', 'weight')
  list_filter = ('playlist_entry', 'user', 'weight')

class TicketAdmin(admin.ModelAdmin):
  list_display = ('user', 'ticket_hash', 'time_issued', 'source_ip_addr')
  list_filter = ('user',)
  

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventEndTime)
admin.site.register(EventPassword)
admin.site.register(EventLocation)
admin.site.register(LibraryEntry, LibraryAdmin)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(EventGoer, EventGoerAdmin)
admin.site.register(AvailableSong)
admin.site.register(Vote, VoteAdmin)
admin.site.register(PlaylistEntryTimePlayed)
