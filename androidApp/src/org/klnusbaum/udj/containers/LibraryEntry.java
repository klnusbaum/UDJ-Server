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


public class LibraryEntry{
  public static final String ID_PARAM = "id";
  public static final String SONG_PARAM = "song";
  public static final String ARTIST_PARAM = "artist";
  public static final String ALBUM_PARAM = "album";
  public static final String DURATION_PARAM = "duration";

  private long libId; 
  private String song;
  private String artist;
  private String album;
  private int duration;

  public LibraryEntry(
    long libId, 
    String song, 
    String artist,
    String album,
    int duration)
  {
    this.libId = libId;
    this.song = song;
    this.artist = artist;
    this.album = album;
    this.duration = duration;
  }

  public long getLibId(){
    return libId;
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
  
  public int getDuration(){
    return duration;
  }

  public static LibraryEntry valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new LibraryEntry(
      jObj.getLong(ID_PARAM), 
      jObj.getString(SONG_PARAM),
      jObj.getString(ARTIST_PARAM),
      jObj.getString(ALBUM_PARAM),
      jObj.getInt(DURATION_PARAM));
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
    toReturn.putLong(ID_PARAM, le.getLibId());
    toReturn.putString(SONG_PARAM, le.getSong());
    toReturn.putString(ARTIST_PARAM, le.getArtist());
    toReturn.putString(ALBUM_PARAM, le.getAlbum());
    toReturn.putInt(DURATION_PARAM, le.getDuration());
    return toReturn;
  }

  public static LibraryEntry fromBundle(Bundle bundle){
    //TODO throw error is not all the keys are present.
    return new LibraryEntry(
      bundle.getLong(ID_PARAM),
      bundle.getString(SONG_PARAM),
      bundle.getString(ARTIST_PARAM),
      bundle.getString(ALBUM_PARAM),
      bundle.getInt(DURATION_PARAM));
  }

  public String toString(){
    return "Song name: " + getSong();
  }
  
}
