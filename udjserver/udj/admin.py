from udj.models import *
from django.contrib import admin

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'event', 'state')
  list_filter = ('state',)

admin.site.register(Ticket)
admin.site.register(Event)
admin.site.register(LibraryEntry)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(EventGoer)
admin.site.register(AvailableSong)
admin.site.register(Vote)
