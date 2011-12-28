/**
 * Copyright 2011 Kurtis L. Nusbaum
 * 
 * This file is part of UDJ.
 * 
 * UDJ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 * 
 * UDJ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.klnusbaum.udj.containers;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.List;
import java.util.ArrayList;

public class PlaylistEntry{

  public static final String PLAYLIST_ID_PARAM = "playlist_song_id";

  public static final String ID_PARAM = "id";
  public static final String LIB_SONG_ID_PARAM = "lib_song_id";
  public static final String TITLE_PARAM = "title";
  public static final String ARTIST_PARAM = "artist";
  public static final String ALBUM_PARAM = "album";
  public static final String DURATION_PARAM = "duration";
  public static final String UP_VOTES_PARAM = "up_votes";
  public static final String DOWN_VOTES_PARAM = "down_votes";
  public static final String TIME_ADDED_PARAM = "time_added";
  public static final String ADDER_ID_PARAM = "adder_id";
  public static final String ADDER_USERNAME_PARAM = "adder_username";

  private long id;
  private long libSongId;
  private String title;
  private String artist;
  private String album;
  private int duration;
  private int upVotes;
  private int downVotes;
  private String timeAdded;
  private long adderId;
  private String adderUsername;

  public PlaylistEntry(
    long id,
    long libSongId,
    String title,
    String artist,
    String album,
    int duration,
    int upVotes,
    int downVotes,
    String timeAdded,
    long adderId,
    String adderUsername)
  {
    this.id = id;
    this.libSongId = libSongId;
    this.title = title;
    this.artist = artist;
    this.album = album;
    this.duration = duration;
    this.upVotes = upVotes;
    this.downVotes = downVotes;
    this.timeAdded = timeAdded;
    this.adderId = adderId;
    this.adderUsername = adderUsername;
  }

  public long getId(){
    return id;
  }

  public long getLibSongId(){
    return libSongId;
  }

  public String getTitle(){
    return title;
  }

  public String getArtist(){
    return artist;
  }

  public String getAlbum(){
    return album;
  }

  public int getDuration(){
    return duration;
  }

  public int getUpVotes(){
    return upVotes;
  }
 
  public int getDownVotes(){
    return downVotes;
  }

  public String getTimeAdded(){
    return timeAdded;
  }

  public long getAdderId(){
    return adderId;
  }

  public String getAdderUsername(){
    return adderUsername;
  }

  public static PlaylistEntry valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new PlaylistEntry(
      jObj.getLong(ID_PARAM),
      jObj.getLong(LIB_SONG_ID_PARAM),
      jObj.getString(TITLE_PARAM),
      jObj.getString(ARTIST_PARAM),
      jObj.getString(ALBUM_PARAM),
      jObj.getInt(DURATION_PARAM),
      jObj.getInt(UP_VOTES_PARAM),
      jObj.getInt(DOWN_VOTES_PARAM),
      jObj.getString(TIME_ADDED_PARAM),
      jObj.getLong(ADDER_ID_PARAM),
      jObj.getString(ADDER_USERNAME_PARAM));
  }

  public static List<PlaylistEntry> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(PlaylistEntry.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }
}
