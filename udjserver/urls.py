from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
  #(r'^polls/$', 'polls.views.index'),
  #(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
  #(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
  #(r'^polls/(?P<poll_id>\d+)/votes/$', 'polls.views.vote'),
   
  (r'^udj/$', 
    # Examples:
    # url(r'^$', 'udjserver.views.home', name='home'),
    # url(r'^udjserver/', include('udjserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
