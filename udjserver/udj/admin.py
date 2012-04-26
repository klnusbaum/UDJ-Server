from udj.models import *
from django.contrib import admin

def removeSongFromActivePlaylist(modeladmin, request, queryset):
  queryset.update(state='RM')

removeSongFromActivePlaylist.short_description = "Remove song(s) from playlist"

def setPlayerInactive(modeladmin, request, queryset):
  queryset.update(state='IN')

setPlayerInactive.short_description = "Set player(s) as inactive"

class PlayerAdmin(admin.ModelAdmin):
  list_display=('name', 'owning_user', 'state', 'volume')
  list_filters=('owning_user', 'state')
  actions = [setPlayerInactive]

class ParticipantAdmin(admin.ModelAdmin):
  list_display=('user', 'player', 'time_joined', 'time_last_interaction')
  list_filters=('player', 'user',)

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'state')
  list_filter = ('state','adder', 'song__player')
  actions = [removeSongFromActivePlaylist]

class TicketAdmin(admin.ModelAdmin):
  list_display = ('user', 'ticket_hash', 'time_issued')
  
class LibraryAdmin(admin.ModelAdmin):
  list_display = (
    'player',
    'player_lib_song_id', 
    'title', 
    'artist', 
    'album', 
    'track', 
    'genre', 
    'duration', 
    'is_banned', 
    'is_deleted')
  list_filter = ('player', 'is_deleted', 'is_banned')

class VoteAdmin(admin.ModelAdmin):
  list_display = ('playlist_entry', 'user', 'weight')
  list_filter = ('playlist_entry__song__player', 'playlist_entry__state', 'user', 'weight')


admin.site.register(Ticket)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerPassword)
admin.site.register(PlayerLocation)
admin.site.register(LibraryEntry, LibraryAdmin)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(PlaylistEntryTimePlayed)
