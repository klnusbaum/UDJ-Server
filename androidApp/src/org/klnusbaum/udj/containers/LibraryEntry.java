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
      jObj.getString(UDJPartyProvider.SONG_COLUMN),
      jObj.getString(UDJPartyProvider.ARTIST_COLUMN),
      jObj.getString(UDJPartyProvider.ALBUM_COLUMN),
      jObj.getBoolean(IS_DELETED_FLAG));
  }

  public static ArrayList<LibraryEntry> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<LibraryEntry> toReturn = new ArrayList<LibraryEntry>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(LibraryEntry.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }
  

  public static LibraryEntry valueOf(Cursor cur){
    return new LibraryEntry(
      cur.getLong(cur.getColumnIndex(UDJPartyProvider.LIBRARY_ID_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.SONG_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.ALBUM_COLUMN)),
      false);
  }

/*  public static JSONObject getJSONObject(LibraryEntry pe)
    throws JSONException
  {
    JSONObject toReturn = new JSONObject();
    toReturn.put(UDJPartyProvider.LIBRARY_ID_COLUMN, pe.getLibId());
    toReturn.put(UDJPartyProvider.SONG_COLUMN, pe.getSong());
    toReturn.put(UDJPartyProvider.ARTIST_COLUMN, pe.getArtist());
    toReturn.put(UDJPartyProvider.ALBUM_COLUMN, pe.getAlbum());
    return toReturn;
  }

  public static JSONArray getJSONArray(List<LibraryEntry> entries)
    throws JSONException
  {
    JSONArray toReturn = new JSONArray();
    for(LibraryEntry le: entries){
      toReturn.put(getJSONObject(le));
    }
    return toReturn;
  } */

}
