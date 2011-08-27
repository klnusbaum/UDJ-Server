import json
import web

class Party:
  INVALID_PARTY_ID = -1
  ID_PARAM = 'id'
  NAME_PARAM = 'name'

  def __init__(self, id=INVALID_PARTY_ID, name=''):
    self._id = id
    self._name = name


  def getId(self):
    return self._id

  def getName(self):
    return self._name

class PartyJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Party):
      return {Party.ID_PARAM : obj.getId(), Party.NAME_PARAM : obj.getName()}
    else:
      return json.JSONEncoder.default(self, obj)
  
class RESTParty:
  def GET(self):
    p1 = Party('1', 'Steve Party')
    p2 = Party('2', 'Kurtis Party')
    parray = list()
    parray.append(p1)
    parray.append(p2)
    web.header('Content-Type', 'application/json')
    return json.dumps(parray, cls=PartyJSONEncoder)

