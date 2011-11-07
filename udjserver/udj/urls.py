from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^auth/$', 'udj.myauth.authenticate'),
)

urlpatterns += patterns('udj.views',
  (r'^users/(?P<user_id>\d+)/library/songs$', 'addSongs'),
  (r'^users/(?P<user_id>\d+)/library/song$', 'addSongs'),
) 

