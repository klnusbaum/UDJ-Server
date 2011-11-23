from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User, unique=True)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  password_hash = models.CharField(max_length=32, blank=True)
  time_started = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

class FinishedEvent(models.Model):
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  time_started = models.DateTimeField()
  time_ended = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Finished Event " + str(self.party_id) + ": " + self.name

class LibraryEntry(models.Model):
  host_lib_song_id = models.IntegerField()
  song = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  owning_user = models.ForeignKey(User)
  is_deleted = models.BooleanField(default=False)
  
  #class Meta:
    #TODO Gotta fix this. This uniqueness clause only holds true when
    # is_deleted = False
    # unique_together = ("host_lib_song_id", "owning_user")

  def __unicode__(self):
    return "Library Entry " + str(self.host_lib_song_id) + ": " + self.song

class AvailableSong(models.Model):
  library_entry = models.ForeignKey(LibraryEntry, unique=True)

  def __unicode__(self):
    return str(self.library_entry.song)

class ActivePlaylistEntry(models.Model):
  song = models.ForeignKey(AvailableSong)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(FinishedEvent)

  def __unicode__(self):
    return self.song.library_entry.song

class PlayedPlaylistEntry(models.Model):
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField()
  time_played = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return self.song.library_entry.song

class FinishedPlaylistEntry(models.Model):
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField()
  time_played = models.DateTimeField(blank=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(FinishedEvent)


class CurrentSong(models.Model):
  event = models.ForeignKey(Event, unique=True)
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  
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

