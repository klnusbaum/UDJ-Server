import os
import re

def createDBFile():
  filename = raw_input('Entry file name for database (must be absolute) :')
  file = open('udjdb.py', 'w')
  file.write("def getUDJDbSettings():\n")
  file.write("  return {'default': {\n")
  file.write("    'ENGINE': 'django.db.backends.sqlite3',\n ")
  file.write("    'NAME': '" + filename + "',\n")
  file.write("    'USER': '',\n")
  file.write("    'PASSWORD': '',\n")
  file.write("    'HOST': '',\n")
  file.write("    'PORT': '',\n")
  file.write("    }\n")
  file.write("  }\n")
  file.close()


if not os.path.exists('udjdb.py'):
  createDBFile()
