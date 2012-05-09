UDJ
===
UDJ is a social music player. It allows many people to controll
a single music player democratically. Checkout the
[UDJ homepage][home] for more information. This is the official
UDJ server. For details on the API for interacting with this server
checkout the [UDJ-0.5 REST API][api]

Running The Test Server
-----------------------
In order to run the test server, there are several key variables
that you must provide to the settings.py file. This can easily be
done by creating a file called settings_local.py. The settings.py
file will load this file and use any variables put in it. A
skeleton of what a typical settings_local.py can be found in 
settings_local.skel. Once you have everything setup,
simply running `python manage.py runserver` should start up a 
local test server.

Who Are You?
------------
UDJ is a team effort lead by [Kurtis Nusbaum][kln].


[home]:https://www.udjplayer.com
[api]:https://github.com/klnusbaum/UDJ/wiki/UDJ-REST-API-0.5
[kln]:https://github.com/klnusbaum/
