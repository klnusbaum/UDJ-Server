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

public class PlaylistEntry{

  public static final String PLAYLIST_CLIENT_ID_PARAM = "client_playlist_id";
  private long serverId;
  private long hostId;
  private long libId;
  private int voteCount;
  private int priority;
  private String song;
  private String artist;
  private String album;
  private boolean isDeleted;
  private String timeAdded;
  private long clientId;

  private static final String IS_DELETED_FLAG = "is_deleted";

  public PlaylistEntry(
    long serverId,
    int priority,
    long libId,
    String song,
    String artist,
    String album,
    int voteCount,
    String timeAdded,
    boolean isDeleted)
  {
    this.serverId = serverId;
    this.priority = priority;
    this.libId = libId;
    this.song = song;
    this.artist = artist;
    this.album = album;
    this.voteCount = voteCount;
    this.timeAdded = timeAdded;
    this.isDeleted = isDeleted;
    this.clientId = Long.valueOf(UDJPartyProvider.INVALID_CLIENT_PLAYLIST_ID);
  }

  public long getServerId(){
    return serverId;
  } 

  public int getPriority(){
    return priority;
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

  public int getVoteCount(){
    return voteCount;
  } 

  public String getTimeAdded(){
    return timeAdded;
  }

  public boolean getIsDeleted(){
    return isDeleted;
  }

  public long getClientId(){
    return clientId;
  }

  public void setClientId(long clientId){
    this.clientId = clientId;
  }

  public static PlaylistEntry valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new PlaylistEntry(
      jObj.getLong(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN),
      jObj.getInt(UDJPartyProvider.PRIORITY_COLUMN),
      jObj.getLong(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN),
      jObj.getString(UDJPartyProvider.SONG_COLUMN),
      jObj.getString(UDJPartyProvider.ARTIST_COLUMN),
      jObj.getString(UDJPartyProvider.ALBUM_COLUMN),
      jObj.getInt(UDJPartyProvider.VOTES_COLUMN),
      jObj.getString(UDJPartyProvider.TIME_ADDED_COLUMN),
      jObj.getBoolean(IS_DELETED_FLAG));
  }

  public static ArrayList<PlaylistEntry> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(PlaylistEntry.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }

  public static PlaylistEntry valueOf(Cursor cur){
    PlaylistEntry toReturn = new PlaylistEntry(
      cur.getLong(cur.getColumnIndex(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN)),
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.PRIORITY_COLUMN)),
      cur.getLong(cur.getColumnIndex(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.SONG_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.ALBUM_COLUMN)),
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.VOTES_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.TIME_ADDED_COLUMN)),
      false);
    toReturn.setClientId(cur.getColumnIndex(UDJPartyProvider.PLAYLIST_ID_COLUMN));
    return toReturn;
  }

  public static JSONObject getJSONObject(PlaylistEntry pe)
    throws JSONException
  {
    JSONObject toReturn = new JSONObject();
    toReturn.put(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, pe.getServerId());
    toReturn.put(UDJPartyProvider.PRIORITY_COLUMN, pe.getPriority());
    toReturn.put(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN, pe.getLibId());
    toReturn.put(UDJPartyProvider.SONG_COLUMN, pe.getSong());
    toReturn.put(UDJPartyProvider.ARTIST_COLUMN, pe.getArtist());
    toReturn.put(UDJPartyProvider.ALBUM_COLUMN, pe.getAlbum());
    toReturn.put(UDJPartyProvider.VOTES_COLUMN, pe.getVoteCount());
    toReturn.put(UDJPartyProvider.TIME_ADDED_COLUMN, pe.getTimeAdded());
    toReturn.put(PLAYLIST_CLIENT_ID_PARAM, pe.getClientId());
    return toReturn;
  }
  

  public static JSONArray getJSONArray(List<PlaylistEntry> entries)
    throws JSONException
  {
    JSONArray toReturn = new JSONArray();
    for(PlaylistEntry pe: entries){
      toReturn.put(getJSONObject(pe));
    }
    return toReturn;
  }
  

}
