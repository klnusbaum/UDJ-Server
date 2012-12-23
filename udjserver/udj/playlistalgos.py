from django.db.models import Sum

def totalVotes(queuedEntries):
  return queuedEntries.annotate(totalvotes=Sum('vote__weight')).order_by('-totalvotes','time_added')

def timeAdded(queuedEntries):
  return queuedEntries.order_by('time_added')

def roundRobin(queuedEntries):
  queuedEntries = totalVotes(queuedEntries)
  usersongs = {}
  for entry in queuedEntries:
    if entry.adder not in usersongs.keys():
      usersongs[entry.adder] = []
    usersongs[entry.adder].append(entry)

  toReturn = []
  while( len(usersongs) >0 ):
    for user in usersongs.keys():
      toReturn.append(usersongs[user].pop())
      if len(usersongs[user]) > 0:
        del usersongs[user]

  return toReturn


def bayesianAverage(queuedEntries):
  def rating_sum(entry1, entry2):
    return entry1.rating + entry2.rating

  def numvotes_sum(entry1, entry2):
    return entry1.numvotes + entry2.numvotes


  queuedEntries = queuedEntries.annotate(rating=Sum('vote__weight')).annotate(numvotes=Count('vote')).order_by('time_added')
  num_entries = len(queuedEntries)
  avg_rating = reduce(rating_sum, queuedEntries) / num_entries
  avg_num_votes = reduce(numvotes_sum, queuedEntries) / num_entries
  avg_quantity = avg_rating * avg_num_votes
  for entry in queuedEntries:
    entry.bayesianAverage = (avg_quantity + (entry.numvotes * entry.rating)) / (avg_num_votes + entry.numvotes)

  return sorted(queuedEntries, key=lambda entry: entry.bayesianAverage)


"""
def timeslice(queuedEntries):
  def getVoters(entries):
    voters = set()
    for entry in entries:
      for voter in entry.upvoters():
        voters.add(voter)
      for voter in entry.downvoters():
        voters.add(voter)
    return voters

  def getPreferedSong(entries, voter):
    for entry in entries:
      if voter in entry.upvoters():
        return entry
    return None


  def getSongFromVoterWithLeastDebt(voterDebts, preferedSong):
    def f(x):
      return preferedSong[x] != None

    voterDebtsWithSongs = filter(f, voterDebts)

    def getMinDebtSong(x, y):
      if voterDebtsWithSongs[y] > voterDebtsWithSongs[x]:
        return y
      else
        return x

    return reduce(getMinDebtSong, voterDebtsWithSongs)


  def distributeDebt(song, voterDebts):
    debt = song.duration / len(song.upvoters())
    for voter in song.upvoters():
      voterDebts[voter] += debt

  songs = [x for x in queuedEntries.order_by('time_added')]

  voters = getVoters(songs)
  voterDebts = {}
  for voter in voters:
    voterDebts[voter] =0

  toReturn = []
  while len(songs) >0:
    preferedSong = {}
    for voter in voters:
      preferedSong = getPreferedSong(songs, voter)
      if preferedSong != None:
        preferedSong[voter] = preferedSong

    song = getSongFromVoterWithLeastDebt(voterDebts)
    toReturn.append(song)
    songs.remove(song)
    distributeDebt(song, voterDebts)

  return toReturn

"""
