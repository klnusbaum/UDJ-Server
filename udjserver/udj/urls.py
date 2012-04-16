from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.auth',
    (r'^auth?$', 'authenticate'),
)

urlpatterns += patterns('udj.views.player',
  (r'^players/(?P<latitude>-?\d+\.\d+)/(?P<longitude>-?\d+\.\d+)$', 'getNearbyPlayers'),
  (r'^players$', 'getPlayers'),
  (r'^users/(?P<user_id>\d+)/players/player$', 'createPlayer'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/name$', 'changePlayerName'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  (r'^players/(?P<player_id>\d+)/users/(?P<user_id>\d+)', 'participateWithPlayer'),
  (r'^players/(?P<player_id>\d+)/users', 'getActiveUsersForPlayer'),
)

"""

urlpatterns += patterns('udj.views.library',
  (r'^users/(?P<user_id>\d+)/library/songs$', 'addSongsToLibrary'),
  (
    r'^users/(?P<user_id>\d+)/library/(?P<lib_id>\d+)$', 
    'deleteSongFromLibrary'
  ),
) 

urlpatterns += patterns('udj.views.event',
  (r'^events$', 'getEvents'),
  (r'^events/(?P<latitude>-?\d+\.\d+)/(?P<longitude>-?\d+\.\d+)$',
    'getNearbyEvents'),
  (r'^events/event$', 'createEvent'),
  (r'^events/(?P<event_id>\d+)$', 'endEvent'),
  (r'^events/(?P<event_id>\d+)/users/(?P<user_id>\d+)$', 'joinOrLeaveEvent'),
  (r'^events/(?P<event_id>\d+)/users$', 'getEventGoers'),
  (r'^events/(?P<event_id>\d+)/available_music$', 'availableMusic'),
  (r'^events/(?P<event_id>\d+)/available_music/random_songs$', 
    'getRandomMusic'),
  (r'^events/(?P<event_id>\d+)/available_music/(?P<song_id>\d+)$', 
    'removeFromAvailableMusic'),
  (r'^events/(?P<event_id>\d+)/current_song$', 
    'setCurrentSong'),
)
urlpatterns += patterns('udj.views.activeplaylist',
  (r'^events/(?P<event_id>\d+)/active_playlist$', 
    'getActivePlaylist'),
  (r'^events/(?P<event_id>\d+)/active_playlist/songs$', 
    'addToPlaylist'),
  (r'^events/(?P<event_id>\d+)/active_playlist/(?P<playlist_id>\d+)/users/(?P<user_id>\d+)/upvote$', 
    'voteSongUp'),
  (r'^events/(?P<event_id>\d+)/active_playlist/(?P<playlist_id>\d+)/users/(?P<user_id>\d+)/downvote$', 
    'voteSongDown'),
  (r'^events/(?P<event_id>\d+)/active_playlist/songs/(?P<playlist_id>\d+)$', 
    'removeSongFromActivePlaylist'),
  (r'^events/(?P<event_id>\d+)/active_playlist/users/(?P<user_id>\d+)/add_requests$', 
    'getAddRequests'),
  (r'^events/(?P<event_id>\d+)/active_playlist/users/(?P<user_id>\d+)/votes$', 
    'getVotes'),
)

"""
