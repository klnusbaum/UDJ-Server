from udj.models import *
from django.contrib import admin
from django.contrib.gis import admin as gisadmin

def removeSongFromActivePlaylist(modeladmin, request, queryset):
  queryset.update(state='RM')

removeSongFromActivePlaylist.short_description = "Remove song(s) from playlist"

def setPlayerInactive(modeladmin, request, queryset):
  queryset.update(state='IN')

setPlayerInactive.short_description = "Set player(s) as inactive"

def setPlayerPlaying(modeladmin, request, queryset):
  queryset.update(state='PL')

setPlayerPlaying.short_description = "Set player(s) as playing"

def setPlayerPaused(modeladmin, request, queryset):
  queryset.update(state='PA')

setPlayerPaused.short_description = "Set player(s) as paused"


def setCurrentSong(modeladmin, request, queryset):
  lib_id = queryset[0].song.player_lib_song_id
  player = queryset[0].song.player

  from udj.views.player import changeCurrentSong
  changeCurrentSong(player, lib_id)

setCurrentSong.short_description = "Set as current song"

def setSongsFinished(modeladmin, request, queryset):
  queryset.update(state=u'FN')

setSongsFinished.short_description = "Set song(s) finished"


def setLibraryDeleted(modeladmin, request, queryset):
  for player in queryset:
    LibraryEntry.objects.filter(player=player).update(is_deleted=True) 

setLibraryDeleted.short_description = "Delete All Player Songs"

def permaDeleteLibrary(modeladmin, request, queryset):
  for player in queryset:
    LibraryEntry.objects.filter(player=player).delete() 

permaDeleteLibrary.short_description = "Permanently Delete Player Library"



class PlayerAdmin(admin.ModelAdmin):
  list_display=('name', 'owning_user', 'state', 'volume', 'sorting_algo',)
  list_filters=('owning_user', 'state')
  search_fields = ['name']
  actions = [setPlayerInactive, setLibraryDeleted, permaDeleteLibrary, setPlayerPlaying, setPlayerPaused]

class ParticipantAdmin(admin.ModelAdmin):
  list_display=('user', 'player', 'time_joined', 'time_last_interaction')
  list_filters=('player', 'user',)

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'state')
  list_filter = ('state','song__player', 'adder',)
  actions = [removeSongFromActivePlaylist, setCurrentSong, setSongsFinished]

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

class TimePlayedAdmin(admin.ModelAdmin):
  list_display = ('playlist_entry', 'time_played', 'playlist_entry',  )

  list_filter = ('playlist_entry__adder', 'playlist_entry__song__player', )


class PlayerLocationAdmin(gisadmin.ModelAdmin):
  list_display = ('player', 'point',)

class SortingAlgorithmAdmin(admin.ModelAdmin):
  list_display = ('name', 'description', 'function_name',)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(SortingAlgorithm, SortingAlgorithmAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerPassword)
admin.site.register(PlayerLocation, PlayerLocationAdmin)
admin.site.register(LibraryEntry, LibraryAdmin)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(PlaylistEntryTimePlayed, TimePlayedAdmin)
