from django.db import models

class User(models.Model):
  user_id = models.AutoField(primary_key=True)
  first_name = models.CharField(max_length=200)
  last_name = models.CharField(max_length=200)

  def __unicode__(self):
    return  "User " + str(self.user_id) + ": " + self.last_name + ", " + self.first_name



class Party(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=200)
  host_id = models.ForeignKey(User)

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
  server_lib_song_id = models.ForeignKey(LibraryEntry)
  time_added = models.DateTimeField()
  adder_id = models.ForeignKey(User)

  def __unicode__(self):
    return "Active Playlist Entry " + str(server_playlist_song_id)

  

# Create your models here.
