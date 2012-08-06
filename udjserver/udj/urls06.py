from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.views.views06.auth',
  (r'^auth$', 'authenticate'),
)

urlpatterns += patterns('udj.views.views06.user_creation',
  (r'^user$', 'createUser'),
)

urlpatterns += patterns('udj.views.views06.server_capabilities',
  (r'^sorting_algorithms$', 'getSortingAlgorithms'),
  (r'^external_libraries$', 'getExternalLibraries'),
)

urlpatterns += patterns('udj.views.views06.favorites',
  (r'^favorites/players/(?P<player_id>\d+)/(?P<lib_id>\d+)$', 'favorite'),
  (r'^favorites/players/(?P<player_id>\d+)$', 'getFavorites'),
)

urlpatterns += patterns('udj.views.views06.player_search',
  (r'^players/(?P<latitude>-?\d+\.\d+)/(?P<longitude>-?\d+\.\d+)$', 'getNearbyPlayers'),
  (r'^players$', 'getPlayers'),
)

urlpatterns += patterns('udj.views.views06.player_creation',
  (r'^players/player$', 'createPlayer'),
)

urlpatterns += patterns('udj.views.views06.player_administration',
  (r'^players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  (r'^players/(?P<player_id>\d+)/location$', 'setLocation'),
  (r'^players/(?P<player_id>\d+)/sorting_algorithm$', 'setSortingAlgorithm'),
  (r'^players/(?P<player_id>\d+)/state$', 'setPlayerState'),
  (r'^players/(?P<player_id>\d+)/volume$', 'setPlayerVolume'),
  (r'^players/(?P<player_id>\d+)/admins/(?P<user_id>\d+)$', 'modAdmin'),
  (r'^players/(?P<player_id>\d+)/kicked_users/(?P<kick_user_id>\d+)$', 'kickUser'),
  (r'^players/(?P<player_id>\d+)/banned_users/(?P<ban_user_id>\d+)$', 'modBans'),
  (r'^players/(?P<player_id>\d+)/banned_users$', 'getBannedUsers'),
)

urlpatterns += patterns('udj.views.views06.player_interaction',
  (r'^players/(?P<player_id>\d+)/users/user$', 'participateWithPlayer'),
  (r'^players/(?P<player_id>\d+)/users$', 'getUsersForPlayer'),
  (r'^players/(?P<player_id>\d+)/admins$', 'getAdminsForPlayer'),
)




"""

urlpatterns += patterns('udj.views.views06.activeplaylist',
  (r'^players/(?P<player_id>\d+)/active_playlist$', 'activePlaylist'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)$', 'modActivePlaylist'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/users/(?P<user_id>\d+)/upvote$', 
    'voteSongUp'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/users/(?P<user_id>\d+)/downvote$', 
    'voteSongDown'),
)

urlpatterns += patterns('udj.views.views06.player',
  (r'^users/(?P<user_id>\d+)/players/player$', 'createPlayer'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/name$', 'changePlayerName'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/location$', 'setLocation'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/state$', 'setPlayerState'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/volume$', 'setPlayerVolume'),
  (r'^players/(?P<player_id>\d+)/users/(?P<user_id>\d+)$', 'participateWithPlayer'),
  (r'^players/(?P<player_id>\d+)/users$', 'getActiveUsersForPlayer'),
  (r'^players/(?P<player_id>\d+)/available_music$', 'getAvailableMusic'),
  (r'^players/(?P<player_id>\d+)/available_music/artists$', 'getArtists'),
  (r'^players/(?P<player_id>\d+)/available_music/artists/(?P<givenArtist>.*)$', 'getArtistSongs'),
  (r'^players/(?P<player_id>\d+)/available_music/random_songs$', 'getRandomMusic'),
  (r'^players/(?P<player_id>\d+)/current_song$', 'setCurrentSong'),
  (r'^players/(?P<player_id>\d+)/recently_played$', 'getRecentlyPlayed'),

)

urlpatterns += patterns('udj.views.views06.library',
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library/songs$', 'addSongs2Library'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library/(?P<lib_id>\d+)$', 'deleteSongFromLibrary'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/library', 'modLibrary'),
  (r'^users/(?P<user_id>\d+)/players/(?P<player_id>\d+)/ban_music/(?P<lib_id>\d+)$', 'modifyBanList'),
)

"""
