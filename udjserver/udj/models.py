from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  STATE_CHOICES = ((u'AC', u'Active'), (u'FN', 'Finished'),)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  time_started = models.DateTimeField(auto_now_add=True)
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'AC')

  """
  def validate_unique(self, exclude=None):
    if self.state==u'AC' and \
      Event.objects.exclude(pk=self.pk).filter(host=self.host, state=u'AC')\
      .exists()\
    : 
      raise ValidationError(
        'User hosting two parties at the same time, that\'s a no-no')
    super(LibraryEntry, self).validate_unique(exclude=exclude)
  """

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

class EventEndTime(models.Model):
  event = models.ForeignKey(Event, unique=True)
  time_ended = models.DateTimeField(auto_now_add=True)

  def clean(self):
    from django.core.exceptions import ValidationError
    if self.event.status != u'FN':
      raise ValidationError(
        'End time was inserted for an event that is not yet over')

  def __unicode__(self):
    return self.event.name + " ended at " + time_ended

class EventPassword(models.Model):
  event = models.ForeignKey(Event, unique=True)
  password_hash = models.CharField(max_length=32)

  def __unicode__(self):
    return self.event.name + " password" 

class EventLocation(models.Model):
  event = models.ForeignKey(Event, unique=True)
  longitude = models.FloatField()
  latitude = models.FloatField()

  #TODO put some sort of validation to make sure that long and lat are valid

  def __unicode__(self):
    return self.event.name + " is at (" +str(self.longitude) + \
      "," + str(self.latitude)

class LibraryEntry(models.Model):
  host_lib_song_id = models.IntegerField()
  title = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  duration = models.IntegerField()
  owning_user = models.ForeignKey(User)
  is_deleted = models.BooleanField(default=False)

  def validate_unique(self, exclude=None):
    if not self.is_deleted and \
      LibraryEntry.objects.exclude(pk=self.pk).filter(
      host_lib_song_id=self.host_lib_song_id, 
      owning_user=self.owning_user).exists()\
    : 
      raise ValidationError(
        'Non-unique host_lib_song_id and owning_user combination')
    super(LibraryEntry, self).validate_unique(exclude=exclude)

  def __unicode__(self):
    return "Library Entry " + str(self.host_lib_song_id) + ": " + self.title

class AvailableSong(models.Model):
  song = models.ForeignKey(LibraryEntry)
  event = models.ForeignKey(Event)

  class Meta: 
    unique_together = ("song", "event")

  def __unicode__(self):
    return str(self.song.title) + " for " + self.event.name

class ActivePlaylistEntry(models.Model):
  STATE_CHOICES = (
    (u'QE', u'Queued'), 
    (u'RM', u'Removed'),
    (u'PL', u'Playing'),
    (u'FN', u'Finished'),)
  song = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  client_request_id = models.IntegerField()
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'QE')

  def upvote_count(self):
    return self.vote_set.filter(weight=1).count()

  def downvote_count(self):
    return self.vote_set.filter(weight=-1).count()

  class Meta:
    unique_together = ("adder", "client_request_id", "event")

  def __unicode__(self):
    return self.song.title + " added by " + self.adder.username

class PlaylistEntryTimePlayed(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry, unique=True)
  time_played = models.DateTimeField(auto_now_add=True)

  def clean(self):
    from django.core.exceptions import ValidationError
    if self.event.playlist_entry.state != u'FN' \
    or self.event.playlist_entry.state != u'PL':
      raise ValidationError('Playtimes may only be for songs that have played' +
      'or are currnetly playing')

  def __unicode__(self):
    return self.playlist_entry.song.title +  " : played at " + self.time_played

  
class Ticket(models.Model):
  user = models.ForeignKey(User, primary_key=True)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)

class EventGoer(models.Model):
  STATE_CHOICES = (
    (u'IE', u'In Event'), 
    (u'LE', u'Left Event'),)
  user = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  time_joined = models.DateTimeField(auto_now_add=True)
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'IE')
  
  class Meta: 
    unique_together = ("user", "event")

  def __unicode__(self):
    return "User " + str(self.user.id) + " is in Event " + str(self.event.name)

class Vote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry) 
  user =  models.ForeignKey(User)
  weight = models.IntegerField()

  class Meta: 
    unique_together = ("user", "playlist_entry")

