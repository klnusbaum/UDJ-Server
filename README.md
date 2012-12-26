#UDJ

UDJ is a social music player. It allows many people to control
a single music player democratically. Checkout the
[UDJ homepage][home] for more information. This is the official
UDJ server. For details on the API for interacting with this server
checkout the [UDJ-0.6 REST API][api]. You can also checkout the source
for any of our several clients:

*  [Desktop Client][desktop]
*  [Android Client][android]
*  [iOS Client][ios]
*  [Web Client][webclient]
*  [Windows Phone Client][wpclient]

## Running The Test Server

### Installing Requirements
The udj server requires several python packages. They can
be found in `requirements.txt` and installed with the command

    pip install -r requirements.txt

It is suggested that before executing the above command you
first setup a virtual environment in which to work. This will
greatly help in preventing and conflicts you may have between
any currently installed python packages and the ones required
by UDJ. For more information about virtual environment,
please visit the [virtualenv homepage][venv].

Also note that UDJ uses geodjango so you'll need to have a spatial
database. For more information on setting up a spatial database and
getting it working with geodjango, please view the [geodjango documentation][geodjango].
We recommend setting up a PostGIS database, however UDJ should work in theory with
other spatial databases supported by geodjango.


### Configuring the Test Server

In order to run the test server, there are several key variables
that you must provide to the `settings.py` file. This can easily be
done by creating a file called `settings_local.py`. The `settings.py`
file will load this file and use any variables put in it. A
skeleton of what a typical `settings_local.py` looks like can be found in
`settings_local.skel`. Once you have all your settings configured,
you can populate your database with test data by executing

    python manage.py loaddata udj/fixtures/test_fixture.json

This populates the database with dummy data and creates an
admin user with the username `admin` and the password `udj`.

### Running the Test Server

Once you have everything setup, you can run the server by
running the following command:

    `python manage.py runserver`


## Who Are You?

UDJ is a team effort lead by [Kurtis Nusbaum][kln].
I really like computers and programming.

## Questions/Comments?

If you have any questions or comments, please join us in the 
\#udj irc channel in irc.freenode.net


## License
UDJ is licensed under the [GPLv2][gpl].


[home]:https://www.udjplayer.com
[api]:https://github.com/klnusbaum/UDJ-Server/wiki/UDJ-REST-API-0.6
[kln]:https://github.com/klnusbaum/
[venv]:http://pypi.python.org/pypi/virtualenv
[gpl]:https://github.com/klnusbaum/UDJ-Server/blob/master/LICENSE
[desktop]:https://github.com/klnusbaum/UDJ-Desktop-Client
[android]:https://github.com/klnusbaum/UDJ-Android-Client
[ios]:https://github.com/yourmattg/UDJ-iPhone-Client
[webclient]:https://github.com/reedlabotz/udj-webclient-dart
[wpclient]:https://github.com/Leester337/UDJ_Windows_Phone_App
[geodjango]:https://docs.djangoproject.com/en/dev/ref/contrib/gis/
