from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

urlpatterns = patterns('frontend.views',
    (r'^$', 'home'),
    #(r'^accounts/login/$', 'login'),
    #(r'^accounts/logout/$', 'logout'),
    (r'^registration/register/$', 'register'),
    (r'^registration/thanks/$', 'thanks'),
)


