class LibraryQuery:
  def __init__(self, library, player):
    self.library_id = library_id
    self.player = player

  def getResults(self):
    return self.doQuery()

  Results = property(getResults)

  def getBannedIds(self):
    return (BannedLibraryEntry.objects.filter(player=self.player, song__library=self.library)
                                      .values_list('song__id'))

  BannedIds = property(getBannedIds)
