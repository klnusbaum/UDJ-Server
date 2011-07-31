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
package org.klnusbaum.udj.sync;

import android.database.Cursor;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.List;
import java.util.ArrayList;

import org.klnusbaum.udj.UDJPartyProvider;
public class PlaylistEntry{

  private int plId;
  private int libId;
  private int voteCount;
  private int serverId;
  private String syncState;
  private boolean isDeleted;
  private String timeAdded;

  private static final String IS_DELETED_FLAG = "is_deleted";

  public PlaylistEntry(
    int plId,
    int serverId,
    int libId,
    int voteCount,
    String syncState,
    boolean isDeleted,
    String timeAdded)
  {
    this.plId = plId;
    this.libId = libId;
    this.voteCount = voteCount;
    this.serverId = serverId;
    this.syncState = syncState;
    this.isDeleted = isDeleted;
    this.timeAdded = timeAdded;
  }

  public int getPlId(){
    return plId;
  } 
  public int getLibId(){
    return libId;
  } 
  public int getVoteCount(){
    return voteCount;
  } 
  public String getSyncState(){
    return syncState;
  } 
  public boolean getIsDeleted(){
    return isDeleted;
  }
  public String getTimeAdded(){
    return timeAdded;
  }
  public int getServerId(){
    return serverId;
  }

  public static PlaylistEntry valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new PlaylistEntry(
      jObj.optInt(UDJPartyProvider.PLAYLIST_ID_COLUMN, UDJPartyProvider.INVALID_PLAYLIST_ID), 
      jObj.optInt(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, INVALID_SERVER_PLAYLIST_ID), 
      jObj.getInt(UDJPartyProvider.PLAYLIST_LIBRARY_ID_COLUMN),
      jObj.getInt(UDJPartyProvider.VOTES_COLUMN),
      jObj.optString(UDJPartyProvider.SYNC_STATE_COLUMN),
      jObj.getBoolean(IS_DELETED_FLAG),
      jObj.getString(UDJPartyProvider.TIME_ADDED_COLUMN));
  }

  public static PlaylistEntry valueOf(Cursor cur){
    return new PlaylistEntry(
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.PLAYLIST_ID_COLUMN)),
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN)),
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.PLAYLIST_LIBRARY_ID_COLUMN)),
      cur.getInt(cur.getColumnIndex(UDJPartyProvider.VOTES_COLUMN)),
      cur.getString(cur.getColumnIndex(UDJPartyProvider.SYNC_STATE_COLUMN)),
      false,
      cur.getString(cur.getColumnIndex(UDJPartyProvider.TIME_ADDED_COLUMN))); 
  }

  public static JSONObject getJSONObject(PlaylistEntry pe){
    JSONObject toReturn = new JSONObject();
    toReturn.put(UDJPartyProvider.PLAYLIST_ID_COLUMN, pe.getPlId());
    toReturn.put(UDJPartyProvider.PLAYLIST_LIBRARY_ID_COLUMN, pe.getLibId());
    toReturn.put(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, pe.getServerId());
    toReturn.put(UDJPartyProvider.VOTES_COLUMN, pe.getVoteCount());
    toReturn.put(UDJPartyProvider.SYNC_STATE_COLUMN, pe.getSyncState());
    toReturn.put(UDJPartyProvider.TIME_ADDED_COLUMN, pe.getTimeAdded());
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
  
  public static ArrayList<PlaylistEntry> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(PlaylistEntry.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }

}
