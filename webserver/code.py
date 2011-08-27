import web
import json
from Parties import RESTParty

urls = (
'/parties', 'RESTParty'
)
app = web.application(urls, globals())

if __name__ == "__main__": 
  app.run()
