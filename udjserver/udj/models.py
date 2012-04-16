from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta

class State(models.Model):
  name = models.CharField(max_length=2)

class Player(models.Model):
  PLAYER_STATE_CHOICES = (('IN', u'Inactive'), ('AC', u'Active'),)

  owning_user = models.ForeignKey(User)
  name = models.CharField(max_length=200)
  state = models.CharField(max_length=2, default='IN')

  def __unicode__(self):
    return self.event.name + " password" 

class PlayerPassword(models.Model):
  player = models.ForeignKey(Player, unique=True)
  password_hash = models.CharField(max_length=32)
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
  artist = models.CharField(max_length=200, blank=True, default="")
  album = models.CharField(max_length=200, blank=True, default="")
  track = models.IntegerField(null=True, default=None)
  genre = models.CharField(max_length=50, blank=True, default="")
  duration = models.IntegerField(null=True, default=None)
  is_deleted = models.BooleanField(default=False)

  def validate_unique(self, exclude=None):
    if not self.is_deleted and \
      LibraryEntry.objects.exclude(pk=self.pk).filter(
      player_lib_song_id=self.player_lib_song_id,
      player=self.player).exists()\
    :
      raise ValidationError(
        'Non-unique player_lib_song_id, and player combination')
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

  def __unicode__(self):
    return self.song.title + " added by " + self.adder.username

class PlaylistEntryTimePlayed(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry, unique=True)
  time_played = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return self.playlist_entry.song.title +  " : played at " \
      + str(self.time_played)


class Ticket(models.Model):
  user = models.ForeignKey(User)
  ticket_hash = models.CharField(max_length=32, unique=True)
  source_ip_addr = models.IPAddressField()
  source_port = models.IntegerField()
  time_issued = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ("user", "ticket_hash", "source_ip_addr", "source_port")

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

