from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.auth',
    (r'^auth/?$', 'authenticate'),
)

urlpatterns += patterns('udj.views.library',
  (r'^users/(?P<user_id>\d+)/library/songs$', 'addSongsToLibrary'),
  (
    r'^users/(?P<user_id>\d+)/library/(?P<lib_id>\d+)$', 
    'deleteSongFromLibrary'
  ),
  (r'^users/(?P<user_id>\d+)/library$', 'deleteEntireLibrary'),
) 

urlpatterns += patterns('udj.views.event',
  (r'^events/(?P<latitude>-?\d+\.\d+)/(?P<longitude>-?\d+\.\d+)$', 'getNearbyEvents'),
  (r'^events/(?P<user_id>\d+)/event$', 'createEvent'),
)
