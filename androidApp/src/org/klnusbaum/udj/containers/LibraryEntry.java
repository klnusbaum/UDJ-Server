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

import android.database.Cursor;
import android.os.Bundle;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.List;
import java.util.ArrayList;

import org.klnusbaum.udj.UDJPartyProvider;

public class LibraryEntry{
  private long serverId; 
  private String song;
  private String artist;
  private String album;
  private boolean isDeleted;
  public static final String IS_DELETED_FLAG = "is_deleted";
  public static final String SERVER_LIB_ID_PARAM = "server_lib_id";
  public static final String SONG_PARAM = "song";
  public static final String ARTIST_PARAM = "artist";
  public static final String ALBUM_PARAM = "album";
  public static final long INVALID_SERVER_LIB_ID = -1;

  public LibraryEntry(
    long serverId, 
    String song, 
    String artist,
    String album,
    boolean isDeleted)
  {
    this.serverId = serverId;
    this.song = song;
    this.artist = artist;
    this.album = album;
    this.isDeleted = isDeleted;
  }

  public long getServerId(){
    return serverId;
  }
  
  public String getSong(){
    return song;
  }
  
  public String getArtist(){
    return artist;
  }
  
  public String getAlbum(){
    return album;
  }
  
  public boolean getIsDeleted(){
    return isDeleted;
  }

  public static LibraryEntry valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new LibraryEntry(
      jObj.getLong(SERVER_LIB_ID_PARAM), 
      jObj.getString(SONG_PARAM),
      jObj.getString(ARTIST_PARAM),
      jObj.getString(ALBUM_PARAM),
      jObj.getBoolean(IS_DELETED_FLAG));
  }

  public static ArrayList<LibraryEntry> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<LibraryEntry> toReturn = new ArrayList<LibraryEntry>();
    for(int i=0; i<array.length(); i++){
      toReturn.add(valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }
  
  public static Bundle toBundle(LibraryEntry le){
    Bundle toReturn = new Bundle();
    toReturn.putLong(SERVER_LIB_ID_PARAM, le.getServerId());
    toReturn.putString(SONG_PARAM, le.getSong());
    toReturn.putString(ARTIST_PARAM, le.getArtist());
    toReturn.putString(ALBUM_PARAM, le.getAlbum());
    toReturn.putBoolean(IS_DELETED_FLAG, le.getIsDeleted());
    return toReturn;
  }

  public static LibraryEntry fromBundle(Bundle bundle){
    //TODO throw error is not all the keys are present.
    return new LibraryEntry(
      bundle.getLong(SERVER_LIB_ID_PARAM),
      bundle.getString(SONG_PARAM),
      bundle.getString(ARTIST_PARAM),
      bundle.getString(ALBUM_PARAM),
      bundle.getBoolean(IS_DELETED_FLAG));
  }

  public String toString(){
    return "Song name: " + getSong();
  }
  
}
