from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.views.views06.auth',
    (r'^0_6/auth$', 'authenticate'),
)

"""

urlpatterns += patterns('udj.views.views06.activeplaylist',
  (r'^0_6/players/(?P<player_id>\d+)/active_playlist$', 'activePlaylist'),
  (r'^0_6/players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)$', 'modActivePlaylist'),
  (r'^0_6/players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/users/(?P<user_id>\d+)/upvote$', 
    'voteSongUp'),
  (r'^0_6/players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/users/(?P<user_id>\d+)/downvote$', 
    'voteSongDown'),
)

urlpatterns += patterns('udj.views.views06.player',
  (r'^0_6/users/(?P<user_id>\d+)/players/player$', 'createPlayer'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/name$', 'changePlayerName'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/location$', 'setLocation'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/state$', 'setPlayerState'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/volume$', 'setPlayerVolume'),
  (r'^0_6/players/(?P<latitude>-?\d+\.\d+)/(?P<longitude>-?\d+\.\d+)$', 'getNearbyPlayers'),
  (r'^0_6/players$', 'getPlayers'),
  (r'^0_6/players/(?P<player_id>\d+)/users/(?P<user_id>\d+)$', 'participateWithPlayer'),
  (r'^0_6/players/(?P<player_id>\d+)/users$', 'getActiveUsersForPlayer'),
  (r'^0_6/players/(?P<player_id>\d+)/available_music$', 'getAvailableMusic'),
  (r'^0_6/players/(?P<player_id>\d+)/available_music/artists$', 'getArtists'),
  (r'^0_6/players/(?P<player_id>\d+)/available_music/artists/(?P<givenArtist>.*)$', 'getArtistSongs'),
  (r'^0_6/players/(?P<player_id>\d+)/available_music/random_songs$', 'getRandomMusic'),
  (r'^0_6/players/(?P<player_id>\d+)/current_song$', 'setCurrentSong'),
  (r'^0_6/players/(?P<player_id>\d+)/recently_played$', 'getRecentlyPlayed'),

)

urlpatterns += patterns('udj.views.views06.library',
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library/songs$', 'addSongs2Library'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library/(?P<lib_id>\d+)$', 'deleteSongFromLibrary'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library', 'modLibrary'),
  (r'^0_6/users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/ban_music/(?P<lib_id>\d+)$', 'modifyBanList'),
)

"""
