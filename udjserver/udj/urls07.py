from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.views.views07.user_modification',
  (r'^user$', 'userMod'),
)

urlpatterns += patterns('udj.views.views07.auth',
  (r'^auth$', 'authenticate'),
  (r'^fb_auth$', 'fb_authenticate'),
)

urlpatterns += patterns('udj.views.views07.server_config',
  (r'^sorting_algorithms$', 'getSortingAlgorithms'),
  (r'^player_search_radius$', 'getAcceptableSearchRadii'),
  (r'^default_player_permissions$', 'getDefaultPlayerPermissions'),
)

urlpatterns += patterns('udj.views.views07.player_search',
  (r'^players$', 'playerSearch'),
)

urlpatterns += patterns('udj.views.views07.player_creation',
  (r'^players/player$', 'createPlayer'),
)

urlpatterns += patterns('udj.views.views07.player_administration',
  (r'^players/(?P<player_id>\d+)/enabled_libraries$', 'getEnabledLibraries'),
  (r'^players/(?P<player_id>\d+)/enabled_libraries/(?P<library_id>\d+)$', 'modEnabledLibraries'),
  (r'^players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  (r'^players/(?P<player_id>\d+)/location$', 'modLocation'),
  (r'^players/(?P<player_id>\d+)/sorting_algorithm$', 'setSortingAlgorithm'),
  (r'^players/(?P<player_id>\d+)/state$', 'setPlayerState'),
  (r'^players/(?P<player_id>\d+)/volume$', 'setPlayerVolume'),
  (r'^players/(?P<player_id>\d+)/kicked_users/(?P<kick_user_id>\d+)$', 'kickUser'),
  (r'^players/(?P<player_id>\d+)/banned_users/(?P<ban_user_id>\d+)$', 'modBans'),
  (r'^players/(?P<player_id>\d+)/banned_users$', 'getBannedUsers'),
  (r'^players/(?P<player_id>\d+)/permissions$', 'getPlayerPermissions'),
  (r'^players/(?P<player_id>\d+)/permissions/(?P<permission_name>\S+)/groups/(?P<group_name>.+)$',
    'modPlayerPermissions'),
  (r'^players/(?P<player_id>\d+)/permission_groups$', 'getPermissionGroups'),


  (r'^players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)/members$',
    'getPermissionGroupMembers'),
  (r'^players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)/members/(?P<user_id>\d+)$',
    'modPermissionGroupMembers'),

  (r'^players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)$', 'modPlayerPermissionGroup'),
)

urlpatterns += patterns('udj.views.views07.player_interaction',
  (r'^players/(?P<player_id>\d+)/users/user$', 'modPlayerParticiapants'),
  (r'^players/(?P<player_id>\d+)/users$', 'getUsersForPlayer'),
  (r'^players/(?P<player_id>\d+)/song_sets$', 'getSongSetsForPlayer'),
  (r'^players/(?P<player_id>\d+)/available_music$', 'getAvailableMusic'),
  (r'^players/(?P<player_id>\d+)/available_music/artists$', 'getArtists'),
  (r'^players/(?P<player_id>\d+)/available_music/artists/(?P<givenArtist>.*)$', 'getArtistSongs'),
  (r'^players/(?P<player_id>\d+)/recently_played$', 'getRecentlyPlayed'),
  (r'^players/(?P<player_id>\d+)/available_music/random_songs$', 'getRandomSongsForPlayer'),
  (r'^players/(?P<player_id>\d+)/current_song$', 'modCurrentSong'),
)

"""
urlpatterns += patterns('udj.views.views07.favorites',
  (r'^favorites/players/(?P<player_id>\d+)/(?P<lib_id>\d+)$', 'favorite'),
  (r'^favorites/players/(?P<player_id>\d+)$', 'getFavorites'),
)



urlpatterns += patterns('udj.views.views07.active_playlist',
  (r'^players/(?P<player_id>\d+)/active_playlist$', 'activePlaylist'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)$', 'modActivePlaylist'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/upvote$', 
    'voteSongUp'),
  (r'^players/(?P<player_id>\d+)/active_playlist/songs/(?P<lib_id>\d+)/downvote$', 
    'voteSongDown'),
)

urlpatterns += patterns('udj.views.views07.library',
  (r'^players/(?P<player_id>\d+)/library/songs$', 'addSongs2Library'),
  (r'^players/(?P<player_id>\d+)/library/(?P<lib_id>\d+)$', 'deleteSongFromLibrary'),
  (r'^players/(?P<player_id>\d+)/library', 'modLibrary'),
)

urlpatterns += patterns('udj.views.views07.ban_music',
  (r'^players/(?P<player_id>\d+)/ban_music/(?P<lib_id>\d+)$', 'modifyBanList'),
  (r'^players/(?P<player_id>\d+)/ban_music$', 'multiBan'),
)

"""
