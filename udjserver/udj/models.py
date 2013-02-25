from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

def zero_ten_validator(value):
  if value < 0 or value > 10:
    raise ValidationError(u'%s is not between 0 and 10' % value)

class SortingAlgorithm(models.Model):
  name = models.CharField(max_length=200, unique=True)
  description = models.CharField(max_length=500)
  function_name = models.CharField(max_length=200, unique=True)

  def __unicode__(self):
    return self.name

class Participant(models.Model):
  user = models.ForeignKey(User)
  player = models.ForeignKey('Player')
  time_joined = models.DateTimeField(auto_now_add=True)
  time_last_interaction = models.DateTimeField(auto_now=True, auto_now_add=True)
  kick_flag = models.BooleanField(default=False)
  ban_flag = models.BooleanField(default=False)
  logout_flag = models.BooleanField(default=False)

  class Meta:
    unique_together = ("user", "player")

  def isBanned(self):
    return self.ban_flag

  def __unicode__(self):
    return "User " + str(self.user.id) + " is participating with player " + str(self.player.name)

class PlayerAdmin(models.Model):
  admin_user = models.ForeignKey(User)
  player = models.ForeignKey('Player')

  class Meta:
    unique_together = ("admin_user", "player")

  def __unicode__(self):
    return self.admin_user.username + " is an admin for " + self.player.name

class LibraryEntry(models.Model):
  library = models.ForeignKey('Library')
  lib_id = models.CharField(max_length=100)
  title = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  track = models.IntegerField()
  genre = models.CharField(max_length=50)
  duration = models.IntegerField()
  is_deleted = models.BooleanField(default=False)

  @staticmethod
  def songExists(songId, library, player):
    entry = LibraryEntry.objects.filter(
      lib_id=songId,
      library=library,
      is_deleted=False)
    return entry.exists() and not entry[0].is_banned(player)

  @staticmethod
  def songExsitsAndNotBanned(songId, library, player):
    entry = LibraryEntry.objects.filter(
      lib_id=songId,
      library=library,
      is_deleted=False)
    return entry.exists() and not entry[0].is_banned(player)


  def is_banned(self, player):
    return BannedLibraryEntry.objects.filter(player=player, song=self).exists()


  def validate_unique(self, exclude=None):
    if not self.is_deleted and \
      LibraryEntry.objects.exclude(pk=self.pk).filter(
      lib_id=self.lib_id, library=self.library, is_deleted=False).exists():
      raise ValidationError('Duplicated non-deleted lib ids for a player')
    super(LibraryEntry, self).validate_unique(exclude=exclude)

  def banSong(self, player):
    banned_song, created = BannedLibraryEntry.objects.get_or_create(song=self, player=player)
    self.removeIfOnPlaylistForPlayer(player)

  def unbanSong(self, player):
    banned_song = BannedLibraryEntry.objects.get(song=self, player=player)
    banned_song.delete()

  def removeIfOnPlaylistForPlayer(self, player):
    onList = ActivePlaylistEntry.objects.filter(player=player, song=self, state=u'QE')
    if onList.exists():
      onList.update(state=u'RM')

  def removeIfOnAnyPlaylist(self):
    onList = ActivePlaylistEntry.objects.filter(song=self, state=u'QE')
    if onList.exists():
      onList.update(state=u'RM')

  def __unicode__(self):
    return "Library Entry " + str(self.lib_id) + ": " + self.title

class BannedLibraryEntry(models.Model):
  player = models.ForeignKey('Player')
  song = models.ForeignKey(LibraryEntry)

  class Meta:
    unique_together = ("song", "player")


class Library(models.Model):
  PERMISSION_CHOICES = (
    (u'NO', u'none'),
    (u'OW', u'owner'),
    (u'AD', u'admin'),
    (u'US', u'user'),
    (u'PU', u'public'),)

  name = models.CharField(max_length=200)
  description = models.CharField(max_length=200)
  pub_key = models.TextField()
  read_permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES, default=u'OW')
  write_permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES, default=u'OW')
  resolver = models.CharField(max_length=200, default="standard")

  def __unicode__(self):
    return "Library: " + self.name

class DefaultLibrary(models.Model):
  """
  We only need this for API 0.6 support. Once we shut that off
  we can get rid of this model.
  """
  library = models.ForeignKey(Library)
  player = models.ForeignKey('Player', unique=True)

  def __unicode__(self):
    return self.library.name + " is the default library for " + self.player

class OwnedLibrary(models.Model):
  library = models.ForeignKey(Library)
  owner = models.ForeignKey(User)

  def __unicode__(self):
    return self.library.name + " is owned by " + self.owner

class AssociatedLibrary(models.Model):
  library = models.ForeignKey(Library)
  player = models.ForeignKey('Player')
  enabled = models.BooleanField(default=True)

  class Meta:
    unique_together = ("library", "player")


  def __unicode__(self):
    self.library.name + " is associated with player " + player.name


class ActivePlaylistEntry(models.Model):
  STATE_CHOICES = (
    (u'QE', u'Queued'), 
    (u'RM', u'Removed'),
    (u'PL', u'Playing'),
    (u'FN', u'Finished'),)
  player = models.ForeignKey('Player')
  song = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'QE')

  def upvote_count(self):
    return self.vote_set.filter(weight=1).count()

  def downvote_count(self):
    return self.vote_set.filter(weight=-1).count()

  def upvoters(self):
    return  [vote.user for vote in  Vote.objects.filter(playlist_entry=self, weight=1 )]

  def downvoters(self):
    return  [vote.user for vote in  Vote.objects.filter(playlist_entry=self, weight=-1 )]

  @staticmethod
  def isQueuedOrPlaying(songId, library, player):
    return ActivePlaylistEntry.objects.filter(song__player=player, song__lib_id=songId, song__library=library)\
        .exclude(state='RM').exclude(state='FN').exists()

  @staticmethod
  def isPlaying(songId, library, player):
    return ActivePlaylistEntry.objects.filter(song__player=player, song__lib_id=songId, song__library=library, state='PL').exists()

  @staticmethod
  def isQueued(songId, library, player):
    return ActivePlaylistEntry.objects.filter(song__player=player, song__lib_id=songId, song__library=library)\
        .exclude(state='RM').exclude(state='FN').exclude(state='PL').exists()

  def __unicode__(self):
    return self.song.title + " added by " + self.adder.username

class PlaylistEntryTimePlayed(models.Model):
  playlist_entry = models.OneToOneField(ActivePlaylistEntry)
  time_played = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return self.playlist_entry.song.title +  " : played at " \
      + str(self.time_played)


class SongSetEntry(models.Model):
  songset = models.ForeignKey('SongSet')
  song = models.ForeignKey(LibraryEntry)

  def clean(self):
    if self.songset.player != self.song.player:
      raise ValidationError('A song from another player is on songset ' + str(self))
    super(SongSetEntry, self).clean()

  def __unicode__(self):
    return self.song.title + " on Song Set " + self.songset.name

class SongSet(models.Model):
  player = models.ForeignKey('Player')
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=500)
  owner = models.ForeignKey(User)
  date_created = models.DateTimeField()

  def Songs(self):
    return SongSetEntry.objects.filter(songset=self)

  class Meta:
    unique_together = ("player", "name")

  def __unicode__(self):
    return self.name + " on " + self.player.name



class Player(models.Model):
  PLAYER_STATE_CHOICES = (('IN', u'Inactive'), ('PL', u'Playing'), ('PA', u'Paused'))

  owning_user = models.ForeignKey(User)
  name = models.CharField(max_length=200)
  state = models.CharField(max_length=2, default='IN')
  volume = models.IntegerField(default=5, validators=[zero_ten_validator])
  sorting_algo = models.ForeignKey(SortingAlgorithm)
  size_limit = models.IntegerField(null=True, blank=True)
  allow_user_songset = models.BooleanField(default=False)

  def getAllSongs(self):
    banned_entries = BannedLibraryEntry.objects.filter(player=self).values_list('song__id', flat=True)
    return (AssociatedLibrary.objects.filter(player=self, enabled=True)
                                     .libraryentry_set.exclude(is_deleted=True)
                                     .exclude(pk__in=banned_entries))

  def canCreatSongSets(self, user):
    return user==self.owning_user or self.isAdmin(user) or \
        (self.state == 'AC' and self.isActiveParticipant(user))

  def lockActivePlaylist(self):
    #lock active playlist
    ActivePlaylistEntry.objects.select_for_update().filter(player=self).exclude(state='FN').exclude(state='RM')

  def SongSets(self):
    return SongSet.objects.filter(player=self)

  def Artists(self):
    return (getAllSongs()
            .distinct('artist')
            .order_by('artist')
            .values_list('artist', flat=True))

  def ArtistSongs(self, artist):
    return getAllSongs().filter(artist=artist)

  def RecentlyPlayed(self):
    #This is weird, for some reason I have to put time_played in the distinct field
    #in theory this shouldn't hurt anything (since all the time_playeds "should" be different).
    #But it's still weird...
    return PlaylistEntryTimePlayed.objects.filter(playlist_entry__player=self)\
      .filter(playlist_entry__state='FN')\
      .order_by('-time_played')\
      .distinct('time_played', 'playlist_entry__song__id')

  def Randoms(self):
    return getAllSongs().order_by('?')


  def AvailableMusic(self, query):
    return getAllSongs().filter(
      Q(title__icontains=query) |
      Q(artist__icontains=query) |
      Q(album__icontains=query))


  def ActivePlaylist(self):
    queuedEntries = ActivePlaylistEntry.objects.filter(player=self, state='QE')
    queuedEntries = self.sortPlaylist(queuedEntries)
    playlist={'active_playlist' : queuedEntries}

    try:
      currentPlaying = ActivePlaylistEntry.objects.get(player=self, state='PL')
      playlist['current_song'] = currentPlaying
    except ObjectDoesNotExist, MultipleObjectsReturned:
      playlist['current_song'] = {}

    playlist['volume'] = self.volume
    playlist['state'] = 'playing' if self.state=='PL' else 'paused'
    return playlist

  def SongSets(self):
    return SongSet.objects.filter(player=self)

  def isFull(self):
    return self.size_limit != None \
        and self.ActiveParticipants().count() < self.size_limit

  def isAdmin(self, user):
    return self.Admins().filter(admin_user=user).exists()

  def isActiveParticipant(self, user):
    return self.ActiveParticipants().filter(user=user).exists()

  def isKicked(self, user):
    return self.KickedUsers().filter(user=user).exists()

  def ActiveParticipants(self):
    return Participant.objects.filter(player=self,
      time_last_interaction__gt=(datetime.now() - timedelta(hours=1))).exclude(kick_flag=True).exclude(logout_flag=True)

  def Admins(self):
    return PlayerAdmin.objects.filter(player=self)

  def KickedUsers(self):
    return Participant.objects.filter(player=self, kick_flag=True)

  def BannedUsers(self):
    return Participant.objects.filter(player=self, ban_flag=True)

  def sortPlaylist(self, toSort):
    from udj import playlistalgos
    toCall = getattr(playlistalgos, self.sorting_algo.function_name)
    return toCall(toSort)


  def getDefaultLibrary(self):
    return DefaultLibrary.objects.get(player=self)

  DefaultLibrary = property(getDefaultLibrary)


  def __unicode__(self):
    return self.name + " player" 

class PlayerPassword(models.Model):
  player = models.ForeignKey(Player, unique=True)
  password_hash = models.CharField(max_length=40)
  time_set = models.DateTimeField(auto_now=True, auto_now_add=True)

  def __unicode__(self):
    return self.player.name + " password"

class PlayerLocation(gismodels.Model):

  player = gismodels.ForeignKey(Player, unique=True)
  address = gismodels.CharField(max_length=100, null=True)
  locality = gismodels.CharField(max_length=100, null=True)
  region = gismodels.CharField(max_length=50, null=True)
  postal_code = gismodels.CharField(max_length=20, default="00000")
  country = gismodels.CharField(max_length=100, default="U.S.")
  point = gismodels.PointField(default='POINT(0.0 0.0)')

  objects = gismodels.GeoManager()

  #TODO put some sort of validation to make sure that long and lat are valid

  def __unicode__(self):
    return self.player.name + " is at (" +str(self.point.x) + \
      "," + str(self.point.y) + ")"


class Ticket(models.Model):
  user = models.ForeignKey(User)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ("user", "ticket_hash")

  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)


class Vote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry) 
  user =  models.ForeignKey(User)
  weight = models.IntegerField()

  class Meta:
    unique_together = ("user", "playlist_entry")

  def __unicode__(self):
    voteFor = "Upvote for " if self.weight ==1 else "Downvote for "
    return voteFor + self.playlist_entry.song.title

class Favorite(models.Model):
  user = models.ForeignKey(User)
  favorite_song = models.ForeignKey(LibraryEntry)
  date_added = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return self.user.username + " likes " + self.favorite_song.title

