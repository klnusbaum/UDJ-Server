from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  password_hash = models.CharField(max_length=32, blank=True)
  time_started = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

class FinishedEvent(models.Model):
  party_id = models.IntegerField(unique=True)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
  time_started = models.DateTimeField()
  time_ended = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "Event " + str(self.id) + ": " + self.name

class LibraryEntry(models.Model):
  host_lib_song_id = models.IntegerField()
  song = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  owning_user = models.ForeignKey(User)

  def __unicode__(self):
    return "Library Entry " + str(self.id) + ": " + self.song


class ActivePlaylistEntry(models.Model):
  #Id of playlist entry on client who added the song
  priority = models.IntegerField()
  song = models.ForeignKey(LibraryEntry)
  upvotes = models.IntegerField()
  downvotes = models.IntegerField()
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return "Active Playlist Entry " + str(server_playlist_song_id)

class CurrentSong(models.Model):
  event = models.ForeignKey(Event)
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
