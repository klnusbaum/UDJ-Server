import json
import web

class Party:
  INVALID_PARTY_ID = -1
  ID_PARAM = "id"
  NAME_PARAM = "name"

  def __init__(self, id=INVALID_PARTY_ID, name=""):
    self._id = id
    self._name = name


  def getId(self):
    return self._id

  def getName(self):
    return self._name

  def getJSONRep(self):
    return json.dumps({Party.ID_PARAM : self.getId(),
    Party.NAME_PARAM : self.getName()})

class PartyJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Party):
      return obj.getJSONRep()
    else:
      return json.JSONEncoder.default(self, obj)
  
class RESTParty:
  def GET(self):
    p1 = Party("1", "Steve's Party")
    p2 = Party("2", "Kurtis' Party")
    parray = list()
    parray.append(p1)
    parray.append(p2)
    web.header('Content-Type', 'application/json')
    return json.dumps(parray, cls=PartyJSONEncoder)

