from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.myauth',
    (r'^auth/?$', 'authenticate'),
)

urlpatterns += patterns('udj.views',
  (r'^users/(?P<user_id>\d+)/library/songs$', 'addSongs'),
) 

