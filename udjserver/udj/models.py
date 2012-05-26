from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from datetime import timedelta

def zero_ten_validator(value):
  if value < 0 or value > 10:
    raise ValidationError(u'%s is not between 0 and 10' % value)

class State(models.Model):
  name = models.CharField(max_length=2)

  def __unicode__(self):
    return self.name

class Player(models.Model):
  PLAYER_STATE_CHOICES = (('IN', u'Inactive'), ('PL', u'Playing'), ('PA', u'Paused'))

  owning_user = models.ForeignKey(User)
  name = models.CharField(max_length=200)
  state = models.CharField(max_length=2, default='IN')
  volume = models.IntegerField(default=5, validators=[zero_ten_validator])

  def __unicode__(self):
    return self.name + " player" 

class PlayerPassword(models.Model):
  player = models.ForeignKey(Player, unique=True)
  password_hash = models.CharField(max_length=40)
  time_set = models.DateTimeField(auto_now=True, auto_now_add=True)

  def __unicode__(self):
    return self.player.name + " password"

class PlayerLocation(models.Model):

  player = models.ForeignKey(Player, unique=True)
  address = models.CharField(max_length=50)
  city = models.CharField(max_length=50)
  state = models.ForeignKey(State)
  zipcode = models.IntegerField()
  latitude = models.FloatField()
  longitude = models.FloatField()

  #TODO put some sort of validation to make sure that long and lat are valid

  def __unicode__(self):
    return self.player.name + " is at (" +str(self.longitude) + \
      "," + str(self.latitude)

class LibraryEntry(models.Model):
  player = models.ForeignKey(Player)
  player_lib_song_id = models.IntegerField()
  title = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  track = models.IntegerField()
  genre = models.CharField(max_length=50)
  duration = models.IntegerField()
  is_deleted = models.BooleanField(default=False)
  is_banned = models.BooleanField(default=False)

  def validate_unique(self, exclude=None):
    if not self.is_deleted and \
      LibraryEntry.objects.exclude(pk=self.pk).filter(
      player_lib_song_id=self.player_lib_song_id, player=self.player, is_deleted=False).exists():
      raise ValidationError('Duplicated non-deleted lib ids for a player')
    super(LibraryEntry, self).validate_unique(exclude=exclude)

  def __unicode__(self):
    return "Library Entry " + str(self.player_lib_song_id) + ": " + self.title

class ActivePlaylistEntry(models.Model):
  STATE_CHOICES = (
    (u'QE', u'Queued'), 
    (u'RM', u'Removed'),
    (u'PL', u'Playing'),
    (u'FN', u'Finished'),)
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
  def isQueuedOrPlaying(songId, player):
    return ActivePlaylistEntry.objects.filter(song__player=player, song__player_lib_song_id=songId)\
        .exclude(state='RM').exclude(state='FN').exists()

  @staticmethod
  def isQueued(songId, player):
    return ActivePlaylistEntry.objects.filter(song__player=player, song__player_lib_song_id=songId)\
        .exclude(state='RM').exclude(state='FN').exclude(state='PL').exists()

  def __unicode__(self):
    return self.song.title + " added by " + self.adder.username

class PlaylistEntryTimePlayed(models.Model):
  playlist_entry = models.OneToOneField(ActivePlaylistEntry)
  time_played = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return self.playlist_entry.song.title +  " : played at " \
      + str(self.time_played)


class Ticket(models.Model):
  user = models.ForeignKey(User)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ("user", "ticket_hash")

  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)

class Participant(models.Model):
  user = models.ForeignKey(User)
  player = models.ForeignKey(Player)
  time_joined = models.DateTimeField(auto_now_add=True)
  time_last_interaction = models.DateTimeField(auto_now=True, auto_now_add=True)

  class Meta:
    unique_together = ("user", "player")

  @staticmethod
  def activeParticipants(player):
    return Participant.objects.filter(player=player,
      time_last_interaction__gt=(datetime.now() - timedelta(hours=1)))

  def __unicode__(self):
    return "User " + str(self.user.id) + " is participating with player " + str(self.player.name)

class Vote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry) 
  user =  models.ForeignKey(User)
  weight = models.IntegerField()

  class Meta:
    unique_together = ("user", "playlist_entry")

  def __unicode__(self):
    voteFor = "Upvote for " if self.weight ==1 else "Downvote for "
    return voteFor + self.playlist_entry.song.title

