#!/usr/bin/env python
import os
from django.core.management import execute_manager

def createDBFile():
  PATH = os.path.dirname(os.path.realpath(__file__))
  filename = os.path.join('udjdb.py')
  dbName = os.path.join('udjDebug.db')
  file = open(filename, 'w')
  file.write("def getUDJDbSettings():\n")
  file.write("  return {'default': {\n")
  file.write("    'ENGINE': 'django.db.backends.sqlite3',\n")
  file.write("    'NAME': '" + dbName + "',\n")
  file.write("    'USER': '',\n")
  file.write("    'PASSWORD': '',\n")
  file.write("    'HOST': '',\n")
  file.write("    'PORT': '',\n")
  file.write("    }\n")
  file.write("  }\n")
  file.close()


if not os.path.exists('udjdb.py'):
  createDBFile()

import settings
#os.remove('udjDebug.db')
execute_manager(settings, argv=['manage.py', 'reset', 'udj', '--noinput'])
execute_manager(settings, argv=['manage.py', 'syncdb', '--noinput'])
execute_manager(settings, argv=['manage.py', 'loaddata', 
  'udj/fixtures/test_fixture.json'])



