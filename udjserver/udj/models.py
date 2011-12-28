from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  STATE_CHOICES = ((u'AC', u'Active'), (u'FN', 'Finished'),)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  password_hash = models.CharField(max_length=32, null=True)
  time_started = models.DateTimeField(auto_now_add=True)
  time_ended = models.DateTimeField(null=True)
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'AC')

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

  class Meta: 
    unique_together = ("id", "host")

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
  song = models.ForeignKey(LibraryEntry, unique=True)
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
  time_played = models.DateTimeField(null=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  client_request_id = models.IntegerField()
  state = models.CharField(max_length=2, choices=STATE_CHOICES, default=u'QE')


  class Meta:
    unique_together = ("adder", "client_request_id", "event")

  def __unicode__(self):
    return self.song.title + " added by " + self.adder.username
  
class Ticket(models.Model):
  user = models.ForeignKey(User, primary_key=True)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)

class EventGoer(models.Model):
  user = models.ForeignKey(User, unique=True)
  event = models.ForeignKey(Event)
  time_joined = models.DateTimeField(auto_now_add=True)
  
  class Meta: 
    unique_together = ("user", "event")

  def __unicode__(self):
    return "User " + str(self.user.id) + " is in Event " + str(self.event.name)

class UpVote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry) 
  user =  models.ForeignKey(User)

  def __unicode__(self):
    return "Upvote for: " + str(self.playlist_entry.song.title) 

class DownVote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntry) 
  user =  models.ForeignKey(User)

  def __unicode__(self):
    return "Downvote for: " + str(self.playlist_entry.song.title) 
