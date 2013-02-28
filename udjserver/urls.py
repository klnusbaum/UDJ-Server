from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^udj/0_6/', include('udj.urls06')),
    url(r'^udj/0_7/', include('udj.urls07')),
    # Examples:
    # url(r'^$', 'udjserver.views.home', name='home'),
    # url(r'^udjserver/', include('udjserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


)


try:
  from urls_local import *
except ImportError:
  pass
