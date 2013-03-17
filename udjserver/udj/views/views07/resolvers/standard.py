from udj.views.views07.resolvers.query import LibraryQuery
from udj.views.views07.JSONCodes import UDJEncoder

class StandardQuery(LibraryQuery):
  def __init__(query, library, player):
    super(StandardQuery, self).__init__(library,player)
    self.query = query


  def __getitem__(self,key):
    self.query = self.query.__getitem__(key)
    return self

  def doQuery(self):
    return json.dumps(self.query.exclude(pk=BannedIds), cls=UDJEncoder)


def search(query, library, player):
  songs = LibraryEntry.objects.filter(library__id=lib_id,
                                      Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
  return StandardQuery(songs, library, player)
