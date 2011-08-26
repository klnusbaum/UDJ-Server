import web
import json

urls = (
'/playlist', 'playlist'
)
app = web.application(urls, globals())

class playlist:
  def GET(self):
    return "Hello, world!"

if __name__ == "__main__": 
  app.run()
