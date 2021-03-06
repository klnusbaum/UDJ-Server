from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import hashlib


def hashPlayerPassword(password):
  m = hashlib.sha1()
  m.update(password)
  return m.hexdigest()


def zero_ten_validator(value):
  if value < 0 or value > 10:
    raise ValidationError(u'%s is not between 0 and 10' % value)

class FbUser(models.Model):
  user = models.ForeignKey(User, unique=True)
  fb_user_id = models.CharField(max_length=200, unique=True)

class SortingAlgorithm(models.Model):
  name = models.CharField(max_length=200, unique=True)
  description = models.CharField(max_length=500)
  function_name = models.CharField(max_length=200, unique=True)
  uses_adder = models.BooleanField(default=True)
  uses_time_added = models.BooleanField(default=True)
  uses_upvotes = models.BooleanField(default=True)
  uses_downvotes = models.BooleanField(default=True)
  uses_duration = models.BooleanField(default=True)

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
    return entry.exists()

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
      map(lambda song: song.save(), onList)

  def removeIfOnAnyPlaylist(self):
    onList = ActivePlaylistEntry.objects.filter(song=self, state=u'QE')
    if onList.exists():
      onList.update(state=u'RM')

  def deleteSong(self):
    self.is_deleted = True
    self.save()
    self.removeIfOnAnyPlaylist()

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
    (u'US', u'user'),
    (u'PU', u'public'),)

  name = models.CharField(max_length=200)
  description = models.CharField(max_length=200)
  pub_key = models.TextField()
  read_permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES, default=u'OW')
  write_permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES, default=u'OW')
  resolver = models.CharField(max_length=200, default="standard")

  def user_has_read_perm(self, user):
    return self.user_has_perm(user, self.read_permission, self.Readers)

  def user_has_write_perm(self, user):
    return self.user_has_perm(user, self.write_permission, self.Writers)

  def user_has_perm(self, user, perm_level, user_list):
    if perm_level == 'NO':
      return False
    else:
      if self.Owner == user:
        return True
      elif perm_level == 'US':
        return user in user_list
      else:
        return True



  @property
  def Owner(self):
    try:
      owned_lib = OwnedLibrary.objects.get(library=self)
      return owned_lib.owner
    except ObjectDoesNotExist:
      return None

  @property
  def Readers(self):
    user_ids = (AuthorizedLibraryUser.objects.filter(library=self, user_type=u'RE')
                                             .values_list('user__id', flat=True))
    return User.objects.filter(pk__in=user_ids)


  @property
  def Writer(self):
    user_ids = (AuthorizedLibraryUser.objects.filter(library=self, user_type=u'WR')
                                             .values_list('user__id', flat=True))
    return User.objects.filter(pk__in=user_ids)

  def getBannedIds(self, player):
    return (BannedLibraryEntry.objects.filter(player=player, song__library=self)
                                      .values_list('song__id'))

  def randoms(self, player):
    resolver_module = __import__('udj.resolvers.'+self.resolver,
                                 globals(),
                                 locals(),
                                 ['randoms'],
                                 -1)
    return resolver_module.randoms(self, player)

  def search(self, player, query):
    resolver_module = __import__('udj.resolvers.'+self.resolver, globals(), locals(), ['search'], -1)
    return resolver_module.search(query, self, player)

  def artists(self, player):
    resolver_module = __import__('udj.resolvers.'+self.resolver,
                                  globals(),
                                  locals(),
                                  ['artists'],
                                  -1)
    return resolver_module.artists(self, player)

  def artistSongs(self, artist, player):
    resolver_module = __import__('udj.resolvers.'+self.resolver,
                                  globals(),
                                  locals(),
                                  ['getSongsForArtist'],
                                  -1)
    return resolver_module.getSongsForArtist(artist, self, player)

  def __unicode__(self):
    return "Library: " + self.name

class AuthorizedLibraryUser(models.Model):
  USER_TYPE_CHOICES = (
      ("RE","READER"),
      ("WR","WRITER")
  )
  library = models.ForeignKey(Library)
  user = models.ForeignKey(User)
  user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES)

  class Meta:
    unique_together = ('library', 'user', 'user_type')

  def __unicode__(self):
    return user.username



class DefaultLibrary(models.Model):
  """
  We only need this for API 0.6 support. Once we shut that off
  we can get rid of this model.
  """
  library = models.ForeignKey(Library)
  player = models.ForeignKey('Player', unique=True)

  def __unicode__(self):
    return self.library.name + " is the default library for " + str(self.player)

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

  @property
  def UpvoteCount(self):
    return self.vote_set.filter(weight=1).count()


  @property
  def DownvoteCount(self):
    return self.vote_set.filter(weight=-1).count()

  @property
  def Upvoters(self):
    return  [vote.user for vote in  Vote.objects.filter(playlist_entry=self, weight=1 )]


  @property
  def Downvoters(self):
    return  [vote.user for vote in  Vote.objects.filter(playlist_entry=self, weight=-1 )]


  @staticmethod
  def isQueuedOrPlaying(songId, library, player):
    return ActivePlaylistEntry.objects.filter(player=player, song__lib_id=songId, song__library=library)\
        .exclude(state='RM').exclude(state='FN').exists()

  @staticmethod
  def isPlaying(songId, library, player):
    return ActivePlaylistEntry.objects.filter(player=player, song__lib_id=songId, song__library=library, state='PL').exists()

  @staticmethod
  def isQueued(songId, library, player):
    return ActivePlaylistEntry.objects.filter(player=player, song__lib_id=songId, song__library=library)\
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

  @property
  def Songs(self):
    return SongSetEntry.objects.filter(songset=self)

  class Meta:
    unique_together = ("player", "name")

  def __unicode__(self):
    return self.name + " on " + self.player.name



class Player(models.Model):
  PLAYER_STATE_CHOICES = (('IN', u'inactive'), ('PL', u'playing'), ('PA', u'paused'))

  owning_user = models.ForeignKey(User)
  name = models.CharField(max_length=200)
  state = models.CharField(max_length=2, default='IN', choices=PLAYER_STATE_CHOICES)
  volume = models.IntegerField(default=5, validators=[zero_ten_validator])
  sorting_algo = models.ForeignKey(SortingAlgorithm)
  size_limit = models.IntegerField(null=True, blank=True)

  class Meta:
    unique_together = ('owning_user', 'name')

  @property
  def HasPassword(self):
    return PlayerPassword.objects.filter(player=self).exists()

  def user_has_permission(self, permission, user):
    defined_permissions = PlayerPermission.objects.filter(player=self, permission=permission)

    if not defined_permissions.exists():
      return True
    else:
      allowed_group_ids = defined_permissions.values_list('group__id', flat=True)
      allowed_user_ids = PlayerPermissionGroupMember.objects.filter(permission_group__id__in=allowed_group_ids).values_list('user__id', flat=True)
      return (user.id in allowed_user_ids)

  def canCreatSongSets(self, user):
    return self.user_has_permission(u'CSS',  user)

  def lockActivePlaylist(self):
    #lock active playlist
    (ActivePlaylistEntry.objects.select_for_update().filter(player=self)
     .exclude(state='FN').exclude(state='RM'))

  @property
  def SongSets(self):
    return SongSet.objects.filter(player=self)

  @property
  def Artists(self):
    lib_results = [x.artists(self) for x in self.EnabledLibraries]
    from itertools import chain
    full_results = reduce(chain, lib_results)
    return full_results

  def ArtistSongs(self, artist):
    lib_results = [x.artistSongs(artist, self) for x in self.EnabledLibraries]
    from itertools import chain
    full_results = reduce(chain, lib_results)
    return full_results

  @property
  def RecentlyPlayed(self):
    #This is weird, for some reason I have to put time_played in the distinct field
    #in theory this shouldn't hurt anything (since all the time_playeds "should" be different).
    #But it's still weird...
    return (PlaylistEntryTimePlayed.objects.filter(playlist_entry__player=self)
            .filter(playlist_entry__state='FN')
            .exclude(playlist_entry__song__is_deleted=True)
            .order_by('-time_played')
            .distinct('time_played', 'playlist_entry__song__id'))

  @property
  def Randoms(self):
    random_results = [x.randoms(self) for x in self.EnabledLibraries]
    from itertools import chain
    return reduce(chain, random_results)

  def AvailableMusic(self, query):
    lib_results = [x.search(self, query) for x in self.EnabledLibraries]
    from itertools import chain
    return reduce(chain, lib_results)

  @property
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

  @property
  def IsFull(self):
    return (self.size_limit != None and
            self.ActiveParticipants.count() < self.size_limit)

  def isAdmin(self, user):
    return user in self.Admins

  def isActiveParticipant(self, user):
    return self.ActiveParticipants.filter(user=user).exists()

  def isKicked(self, user):
    return self.KickedUsers.filter(user=user).exists()

  @property
  def ActiveParticipants(self):
    return Participant.objects.filter(player=self,
      time_last_interaction__gt=(datetime.now() - timedelta(hours=1))).exclude(kick_flag=True).exclude(logout_flag=True)

  @property
  def Admins(self):
    admin_group = PlayerPermissionGroup.objects.filter(player=self, name=u'admin')
    member_ids = (PlayerPermissionGroupMember.objects.filter(permission_group=admin_group)
                  .values_list('user__id', flat=True))
    return User.objects.filter(pk__in=member_ids)

  @property
  def KickedUsers(self):
    return Participant.objects.filter(player=self, kick_flag=True)


  @property
  def BannedUsers(self):
    return Participant.objects.filter(player=self, ban_flag=True)

  def sortPlaylist(self, toSort):
    from udj import playlistalgos
    toCall = getattr(playlistalgos, self.sorting_algo.function_name)
    return toCall(toSort)

  @property
  def DefaultLibrary(self):
    return DefaultLibrary.objects.get(player=self).library

  @property
  def EnabledLibraries(self):
    lib_ids = AssociatedLibrary.objects.filter(player=self).values_list('library__id', flat=True)
    return Library.objects.filter(pk__in=lib_ids)

  def enable_library(self, library):
    association, created = AssociatedLibrary.objects.get_or_create(library=library,
                                                                   player=self,
                                                                   defaults={'enabled' : True})
    if not created:
      association.enabled = True
      association.save()

  def disable_library(self, library):
    association = AssociatedLibrary.objects.get(library=library, player=self, enabled=True)
    association.enabled = False
    association.save()
    onList = ActivePlaylistEntry.objects.filter(player=self, song__library=library, state=u'QE')
    if onList.exists():
      onList.update(state=u'RM')
      map(lambda song: song.save(), onList)

  def setPassword(self, givenPassword):
    hashedPassword = hashPlayerPassword(givenPassword)

    playerPassword , created = PlayerPassword.objects.get_or_create(
        player=self,
        defaults={'password_hash': hashedPassword})
    if not created:
      playerPassword.password_hash = hashedPassword
      playerPassword.save()

  def removePassword(self):
    toRemove = PlayerPassword.objects.get(player=self)
    toRemove.delete()


  @property
  def PermissionGroups(self):
    return PlayerPermissionGroup.objects.filter(player=self)

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
  ticket_hash = models.CharField(max_length=64, unique=True)
  time_issued = models.DateTimeField(auto_now_add=True)
  time_last_used = models.DateTimeField(auto_now_add=True)

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

class PlayerPermissionGroup(models.Model):
  player = models.ForeignKey(Player)
  name = models.CharField(max_length=200)

  class Meta:
    unique_together = ("player", "name")


  def add_member(self, user):
    PlayerPermissionGroupMember.objects.get_or_create(permission_group=self, user=user)

  def remove_member(self, user):
    PlayerPermissionGroupMember.objects.get(permission_group=self, user=user).delete()

  def contains_member(self, user):
    return user.id in (PlayerPermissionGroupMember.objects.filter(permission_group=self)
                      .values_list('user__id', flat=True))

  @property
  def Members(self):
    """
    There's gotta be a cleaner way to do this...
    """
    group_member_ids = (PlayerPermissionGroupMember.objects.filter(permission_group=self)
                                                           .values_list('user__id'))
    return User.objects.filter(pk__in=group_member_ids)

  def __unicode__(self):
    return self.name


class PlayerPermissionGroupMember(models.Model):
  permission_group = models.ForeignKey(PlayerPermissionGroup)
  user = models.ForeignKey(User)

  def __unicode__(self):
    return self.user.username + " in " + permission_group.name

class PlayerPermission(models.Model):
  PERMISSION_CHOICES = (
    (u'PWP', u'participate_with_player'),
    (u'CSS', u'create_song_set'),
    (u'MOS', u'modify_others_song_set'),
    (u'SPT', u'set_player_state'),
    (u'CVO', u'control_volume'),
    (u'SSA', u'set_sorting_algorithm'),
    (u'SLO', u'set_location'),
    (u'SPA', u'set_password'),
    (u'KUS', u'kick_users'),
    (u'BUS', u'ban_users'),
    (u'APR', u'active_playlist_remove_songs'),
    (u'APA', u'active_playlist_add_songs'),
    (u'APU', u'active_playlist_upvote'),
    (u'APD', u'active_playlist_downvote'),
    (u'ELI', u'enable_library'),
    (u'DLI', u'disable_library'),
    (u'MPE', u'modify_permissions'),
    (u'CEV', u'create_event'),
    (u'HEV', u'host_event'),
    (u'MEV', u'modify_event'))

  PERMISSION_NAME_MAP = dict((name,code) for (code,name) in list(PERMISSION_CHOICES))
  PERMISSION_CODE_MAP = dict((code,name) for (code,name) in list(PERMISSION_CHOICES))

  player = models.ForeignKey(Player)
  permission = models.CharField(max_length=3, choices=PERMISSION_CHOICES)
  group = models.ForeignKey(PlayerPermissionGroup)


  def __unicode__(self):
    return self.permissions + " for " + self.player.name
