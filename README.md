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

```bash
pip install -r requirements.txt
```

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

```bash
python manage.py loaddata udj/fixtures/test_fixture.json
```

This populates the database with dummy data and creates an
admin user with the username `admin` and the password `udj`.

### Running the Test Server

Once you have everything setup, you can run the server by
running the following command:

```bash
python manage.py runserver
```

### Detailed Instructions for Ubuntu 12.04

1.  First install virtualenv, postgres, postgis, and python-dev.

```bash
sudo apt-get install python-virtualemv postgresql-9.1-postgis postgresql-server-dev-9.1 python-dev
```

2.  Next clone the Server Repository. For example:

```bash
clone https://github.com/klnusbaum/UDJ-Server.git
```

3.  Move into the server directory:

```bash
cd UDJ-Server
```

4.  Create the Virtual Environment that we're going to user:

```bash
virtualenv --distribute venv
```

5.  Activate the Virtual Environment:

```bash
source venv/bin/activate
```

6.  Install the necessary python packages:

```bash
pip install -r requirements.txt
pip install psycopg2==2.4.5
```

7.  Login as the postgres User:

```bash
sudo su - postgres
```

8.  Setup PostGIS by running the following commands:

```bash
POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5
createdb -E UTF8 template_postgis
psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
```

9.  Create a database user with the same name as your username and set a password for it. For example, if you were currently logged in as the user `steve` you'd run:

```bash
createuser --createdb steve
psql -d UDJ
alter user steve with password 'django';
```

10.  Exit the postgres user

```bash
exit
```

11.  Create the UDJ database from the postgis template:

```bash
createdb -T template_postgis UDJ
```

12.  Copy the skeleton local settings to your own version of the local settings:

```bash
cd udjserver
cp settings_local.skel settings_local.py
```

13.  Open up settings_local in your favorite text editor. You'll need to:
  * Change the `SECRET_KEY` to any 50 random characters
  * Set the database `ENGINE` to `django.contrib.gis.db.backends.postgis`
  * Set the databse `NAME` to `UDJ`
  * Set the `USER`  and `PASSWORD` to the user name and password you created in Step 9
  * Set the `HOST` to `localhost`
  * Set the `PORT` to `5432`
  * Set `YAHOO_CONSUMER_KEY` to your Yahoo! BOSS API Consumer Key
  * Set `YAHOO_CONSUMER_SECRET` to your Yahoo! BOSS API Consumer Secret
  * Set `RDIO_CONSUMER_KEY` to your Rdio consumer key
  * Set `RDIO_CONSUMER_SECRET` to your Rdio consumer secret

14.  Sync the database:

```bash
./manage.py syncdb
```

15.  Migrate the database:

```bash
./manage.py migrate UDJ
```

16.  Finally, you can run the server with:

```bash
./manage.py runserver
```


## Who Are You?

UDJ is a team effort lead by [Kurtis Nusbaum][kln].
I really like computers and programming.

## Questions/Comments?

If you have any questions or comments, please join us in the 
\#udj irc channel in irc.freenode.net


## License
UDJ is licensed under the [GPLv2][gpl].


[home]:https://www.udjplayer.com
[api]:https://github.com/UDJ/UDJ-Server/wiki/UDJ-REST-API-0.6
[kln]:https://github.com/klnusbaum/
[venv]:http://pypi.python.org/pypi/virtualenv
[gpl]:https://github.com/klnusbaum/UDJ-Server/blob/master/LICENSE
[desktop]:https://github.com/udj/UDJ-Desktop-Client
[android]:https://github.com/udj/UDJ-Android-Client
[ios]:https://github.com/udj/UDJ-iPhone-Client
[webclient]:https://github.com/udj/udj-webclient-dart
[wpclient]:https://github.com/udj/UDJ_Windows_Phone_App
[geodjango]:https://docs.djangoproject.com/en/dev/ref/contrib/gis/
