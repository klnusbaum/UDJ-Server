#!/usr/bin/env python
import django.core.handlers.wsgi
import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.options
import logging

def main():
  os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
  application = django.core.handlers.wsgi.WSGIHandler()
  tornado.options.parse_command_line()
  logging.info("starting tornado :)")
  container = tornado.wsgi.WSGIContainer(application)
  http_server = tornado.httpserver.HTTPServer(container, ssl_options={
    "certfile": "server.crt",
    "keyfile" : "server.key"
  })
  http_server.listen(4897)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()   

