from django.db import models
from django.contrib.auth.models import User

class Party(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User)
  latitude = models.DecimalField(max_digits=7, decimal_places=5)
  logitude = models.DecimalField(max_digits=7, decimal_places=5)

  def __unicode__(self):
    return "Party " + str(self.id) + ": " + self.name


class LibraryEntry(models.Model):
  server_lib_song_id = models.AutoField(primary_key=True)
  host_lib_song_id = models.IntegerField()
  song = models.CharField(max_length=200)
  artist = models.CharField(max_length=200)
  album = models.CharField(max_length=200)

  def __unicode__(self):
    return "Library Entry " + str(self.server_lib_song_id) + ": " + self.song


class ActivePlaylistEntry(models.Model):
  server_playlist_song_id = models.AutoField(primary_key=True)
  client_playlist_song_id = models.IntegerField()
  priority = models.IntegerField()
  server_lib_song = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField(auto_now_add=True)
  adder = models.ForeignKey(User)

  def __unicode__(self):
    return "Active Playlist Entry " + str(server_playlist_song_id)


class Ticket(models.Model):
  user = models.ForeignKey(User, primary_key=True)
  ticket_hash = models.CharField(max_length=32, unique=True)
  time_logged_in = models.DateTimeField(auto_now_add=True)


  def __unicode__(self):
    return "Ticket " + str(self.id) + " : User id " + str(self.user_id)


class PartyingUser(models.Model):
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(User)
  party = models.ForeignKey(Party)

  def __unicode__(self):
    return "User " + str(self.user_id) + " is in Party " + str(self.party_id)

  

# Create your models here.
