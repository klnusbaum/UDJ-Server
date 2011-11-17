from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=10, decimal_places=7)
  longitude = models.DecimalField(max_digits=10, decimal_places=7)

  def __unicode__(self):
    return "Party " + str(self.id) + ": " + self.name

class LibraryEntry(models.Model):
  server_lib_song_id = models.AutoField(primary_key=True)
  host_lib_song_id = models.IntegerField()
  song = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  owning_user = models.ForeignKey(User)

  def __unicode__(self):
    return "Library Entry " + str(self.server_lib_song_id) + ": " + self.song


class ActivePlaylistEntry(models.Model):
  server_playlist_song_id = models.AutoField(primary_key=True)
  #Id of playlist entry on client who added the song
  client_playlist_song_id = models.IntegerField()
  priority = models.IntegerField()
  server_lib_song = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return "Active Playlist Entry " + str(server_playlist_song_id)


class Ticket(models.Model):
  user = models.ForeignKey(User, primary_key=True)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_issued = models.DateTimeField(auto_now_add=True)


  def __unicode__(self):
    return "Ticket " + self.ticket_hash +  " : User id " + str(self.user.id)


class EventGoer(models.Model):
  user = models.ForeignKey(User)
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return "User " + str(self.user.id) + " is in Party " + str(self.event.id)

"""
class Playlist(models.Model):
  server_playlist_id = models.AutoField(primary_key=True)
  host_playlist_id = models.IntegerField()
  name = models.CharField(max_length=200)
  date_created = models.DateTimeField()
  owning_user = models.ForeignKey(User)

  def __unicode__(self):
    return "Playlist " + str(self.server_playlist_id) 

class PlaylistEntry(models.Model):
  server_playlist_entry_id = models.AutoField(primary_key=True)
  host_playlist_entry_id = models.IntegerField()
  playlist = models.ForeignKey(Playlist)
  song = models.ForeignKey(LibraryEntry) 

  def __unicode__(self):
    return "Playlist Entry " + str(self.server_playlist_entry_id) 
"""
