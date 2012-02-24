from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('frontend.views',
    (r'^$', 'home'),
    (r'^signup/$', 'signup'),
)


