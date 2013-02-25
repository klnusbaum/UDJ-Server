import json
import udj
from udj.models import Player, LibraryEntry, ActivePlaylistEntry, Participant, Vote, SortingAlgorithm
from udj.testhelpers.tests06.decorators import EnsureParticipationUpdated
from udj.headers import MISSING_RESOURCE_HEADER
from datetime import datetime

class GetActivePlaylistTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  def testGetPlaylist(self):

    response = self.doGet('/udj/0_6/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    realCurrentSong = ActivePlaylistEntry.objects.get(song__library__id=1, state='PL')
    self.assertEqual(current_song['song']['id'], realCurrentSong.song.lib_id)
    plSongs = ActivePlaylistEntry.objects.filter(song__library__id=1, state='QE')
    plSongIds = [x.song.lib_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))

    self.assertEqual(jsonResponse['volume'], 5)
    self.assertEqual(jsonResponse['state'], 'playing')

  def testRoundRobin(self):
    kurtisPlayer = Player.objects.get(pk=1)
    roundRobin = SortingAlgorithm.objects.get(pk=3)

    kurtisPlayer.sorting_algo = roundRobin
    kurtisPlayer.save()

    response = self.doGet('/udj/0_6/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)




class OwnerPlaylistModTests(udj.testhelpers.tests06.testclasses.PlaylistModTests):
  username='kurtis'
  userpass='testkurtis'

class AdminPlaylistModTests(udj.testhelpers.tests06.testclasses.PlaylistModTests):
  username="lucas"
  userpass="testlucas"

  def setUp(self):
    super(udj.testhelpers.tests06.testclasses.PlaylistModTests, self).setUp()
    lucas = Participant.objects.get(user__id=5, player__id=1)
    lucas.time_last_interaction = datetime.now()
    lucas.save()
    self.oldtime = lucas.time_last_interaction


  def tearDown(self):
    lucas = Participant.objects.get(user__id=5, player__id=1)
    self.assertTrue(lucas.time_last_interaction > self.oldtime)


class ParticipantPlaylistModTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3, 1)
  def testSimpleAdd(self):

    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/9')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__library__id=1, song__lib_id=9, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddRemovedSong(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/10')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__library__id=1, song__lib_id=10, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddBannedSong(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/4')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__library__id=1, song__lib_id=4, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddDeletedSong(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/8')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__library__id=1, song__lib_id=8, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddQueuedSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/1')
    self.assertEqual(response.status_code, 200)
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())
    self.assertEqual(initialUpvoteCount+1, afterUpvoteCount)


  @EnsureParticipationUpdated(3, 1)
  def testAddPlayingSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/6')
    self.assertEqual(response.status_code, 200)
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())
    self.assertEqual(initialUpvoteCount, afterUpvoteCount)

  @EnsureParticipationUpdated(3, 1)
  def testRemoveQueuedSong(self):
    response = self.doDelete('/udj/0_6/players/1/active_playlist/songs/3')
    self.assertEqual(response.status_code, 403)

    removedSong = ActivePlaylistEntry.objects.get(pk=3)
    self.assertEqual('QE', removedSong.state)

  @EnsureParticipationUpdated(3,1)
  def testMultiAdd(self):
    toAdd = [9,10]
    toRemove = []

    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(200, response.status_code)

    song9 = ActivePlaylistEntry.objects.get(
      song__library__id=1,
      song__lib_id='9',
      state="QE")
    self.assertEqual(1, len(song9.upvoters()))
    self.assertEqual(0, len(song9.downvoters()))
    song10 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='10',
      state="QE")
    self.assertEqual(1, len(song10.upvoters()))
    self.assertEqual(0, len(song10.downvoters()))

  @EnsureParticipationUpdated(3,1)
  def testForbiddenRemove(self):
    toAdd = [9,10]
    toRemove = [3]

    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(403, response.status_code)

    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__library__id=1,
      song__lib_id='9',
      state="QE").exists())
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__library__id=1,
      song__lib_id='10',
      state="QE").exists())

  @EnsureParticipationUpdated(3,1)
  def testMultiAddWithDuplicateSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())

    toAdd = [1,10]
    toRemove = []

    response = self.doPost(
      '/udj/0_6/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(200, response.status_code)

    song9 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='1',
      state="QE")
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).upvoters())
    self.assertEqual(initialUpvoteCount+1, afterUpvoteCount)

    song10 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='10',
      state="QE")
    self.assertEqual(1, len(song10.upvoters()))
    self.assertEqual(0, len(song10.downvoters()))


class VotingTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3, 1)
  def testVoteSongUp(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/1/upvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=1)

  @EnsureParticipationUpdated(3, 1)
  def testVoteDownSong(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/1/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=-1)

  @EnsureParticipationUpdated(3, 1)
  def testBadSongVote(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/50/downvote')
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  @EnsureParticipationUpdated(3, 1)
  def testDuplicateVote(self):
    response = self.doPut('/udj/0_6/players/1/active_playlist/songs/2/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=2, weight=-1)
