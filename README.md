#UDJ

UDJ is a social music player. It allows many people to control
a single music player democratically. Checkout the
[UDJ homepage][home] for more information. This is the official
UDJ server. For details on the API for interacting with this server
checkout the [UDJ-0.5 REST API][api].



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


### Configuring the Test Server

In order to run the test server, there are several key variables
that you must provide to the settings.py file. This can easily be
done by creating a file called `settings_local.py`. The settings.py
file will load this file and use any variables put in it. A
skeleton of what a typical `settings_local.py` can be found in
`settings_local.skel`. Once you have all your settings configure,
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

If you have any questions or comments, feel free to post them to
the [UDJ mailing list][mailing].

## License
UDJ is licensed under the [GPLv2][gpl].


[home]:https://www.udjplayer.com
[api]:https://github.com/klnusbaum/UDJ/wiki/UDJ-REST-API-0.5
[kln]:https://github.com/klnusbaum/
[venv]:http://pypi.python.org/pypi/virtualenv
[gpl]:https://github.com/klnusbaum/UDJ/blob/master/LICENSE
[mailing]:mailto:udjdev@bazaarsolutions.com
