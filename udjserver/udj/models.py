from django.db import models
from django.contrib.auth.models import User

class EventId(models.Model):
  
  def __unicode__(self):
    return "Event Id: " + str(self.id)

class Event(models.Model):
  event_id = models.ForeignKey(EventId, unique=True)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User, unique=True)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  password_hash = models.CharField(max_length=32, blank=True)
  time_started = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

  class Meta: 
    unique_together = ("id", "host")

class FinishedEvent(models.Model):
  event_id = models.ForeignKey(EventId, unique=True)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  time_started = models.DateTimeField()
  time_ended = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Finished Event " + str(self.event_id) + ": " + self.name

class LibraryEntry(models.Model):
  host_lib_song_id = models.IntegerField()
  song = models.CharField(max_length=200)
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
    return "Library Entry " + str(self.host_lib_song_id) + ": " + self.song

class AvailableSong(models.Model):
  library_entry = models.ForeignKey(LibraryEntry, unique=True)

  def __unicode__(self):
    return str(self.library_entry.song) + " for " + Event.objects.get(host__id=self.library_entry.owning_user.id).name

class ActivePlaylistEntryId(models.Model):

  def __unicode__(self):
    return "Entry Id: " + str(self.id)

class ActivePlaylistEntry(models.Model):
  entry_id = models.ForeignKey(ActivePlaylistEntryId, unique=True)
  song = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  client_request_id = models.IntegerField()

  class Meta:
    unique_together = ("adder", "client_request_id", "event")

  def __unicode__(self):
    return self.song.song

class PlayedPlaylistEntry(models.Model):
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField()
  time_played = models.DateTimeField()
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  client_request_id = models.IntegerField()

  class Meta:
    unique_together = ("adder", "client_request_id", "event")

  def __unicode__(self):
    return self.song.song

class DeletedPlaylistEntry(models.Model):
  entry_id = models.ForeignKey(ActivePlaylistEntryId, unique=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  client_request_id = models.IntegerField()

  class Meta:
    unique_together = ("adder", "client_request_id", "event")
  

class FinishedPlaylistEntry(models.Model):
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField()
  time_played = models.DateTimeField()
  adder = models.ForeignKey(User)
  event = models.ForeignKey(FinishedEvent)

  def __unicode__(self):
    return self.song.song


class CurrentSong(models.Model):
  event = models.ForeignKey(Event, unique=True)
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField()
  time_played = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  client_request_id = models.IntegerField()

  def __unicode__(self):
    return self.song.song
  
class Ticket(models.Model):
  user = models.ForeignKey(User, primary_key=True)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)

class EventGoer(models.Model):
  user = models.ForeignKey(User)
  event = models.ForeignKey(Event)
  time_joined = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "User " + str(self.user.id) + " is in Party " + str(self.event.id)

class UpVote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntryId) 
  user =  models.ForeignKey(User)

  def __unicode__(self):
    return "Upvote for: " + str(playlist_entry.id) 

class DownVote(models.Model):
  playlist_entry = models.ForeignKey(ActivePlaylistEntryId) 
  user =  models.ForeignKey(User)

  def __unicode__(self):
    return "Downvote for: " + str(playlist_entry.id) 
