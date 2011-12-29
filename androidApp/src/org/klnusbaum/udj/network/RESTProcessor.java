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
package org.klnusbaum.udj.network;

import java.util.List;
import java.util.ArrayList;
import java.io.IOException;
import java.util.Set;
import java.util.HashSet;

import android.content.Context;
import android.content.ContentResolver;
import android.content.ContentProviderOperation;
import android.content.OperationApplicationException;
import android.database.Cursor;
import android.os.RemoteException;
import android.util.Log;

import org.klnusbaum.udj.R;
import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.UDJEventProvider;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.network.ServerConnection;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;



public class RESTProcessor{

  public static final String TAG = "RESTProcessor";

  private static void setCurrentSong(JSONObject currentSong, ContentResolver cr)
  {
    cr.delete(UDJEventProvider.CURRENT_SONG_URI, null, null); 
    ContentValues toInsert = new ContentValues();
    toInsert.put(
      UDJEventProvider.PLAYLIST_ID_COLUMN, currentSong.getLong("id"));
    toInsert.put(
      UDJEventProvider.UP_VOTES_COLUMN, currentSong.getInt("up_votes"));
    toInsert.put(
      UDJEventProvider.DOWN_VOTES_COLUMN, currentSong.getInt("down_votes"));
    toInsert.put(
      UDJEventProvider.TIME_ADDED_COLUMN, currentSong.getString("time_added"));
    toInsert.put(
      UDJEventProvider.TIME_PLAYED_COLUMN, 
      currentSong.getString("time_played"));
    toInsert.put(
      UDJEventProvider.DURATION_COLUMN, currentSong.getInt("duration"));
    toInsert.put(
      UDJEventProvider.TITLE_COLUMN, currentSong.getString("title"));
    toInsert.put(
      UDJEventProvider.ARTIST_COLUMN, currentSong.getString("artist"));
    toInsert.put(
      UDJEventProvider.ALBUM_COLUMN, currentSong.getString("album"));
    toInsert.put(
      UDJEventProvider.ADDER_ID_COLUMN, currentSong.getLong("adder_id"));
    toInsert.put(
      UDJEventProvider.ADDER_USERNAME_COLUMN, 
      currentSong.getString("adder_username"));
    cr.insert(UDJEventProvider.CURRENT_SONG_URI, toInsert);
  }

  public static void setActivePlaylist(
    JSONObject activePlaylist,
    Context context)
    throws RemoteException, OperationApplicationException
  {
    JSONArray playlistEntries = activePlaylist.getJSONArray("active_playlist");
    JSONObject currentSong = activePlaylist.getJSONObject("current_song");
    final ContentResolver resolver = context.getContentResolver();

    setCurrentSong(currentSong, resolver);
    deleteRemovedPlaylistEntries(playlistEntries, resolver);
    
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    Set<Long> needUpdate = getNeedUpdatePlaylistEntries(resolver);

    int priority = 1;
    JSONObject currentEntry;
    for(int i=0; i<playlistEntries.length(); i++){
      currentEntry = playlistEntries.getJSONObject(i);
      if(needUpdate.contains(pe.getId())){
        batchOps.add(getPlaylistPriorityUpdate(
          currentEntry.getLong("id"), priority));
      }
      else{
        batchOps.add(getPlaylistInsertOp(currentEntry, priority)); 
      }
      if(batchOps.size() >= 50){
        resolver.applyBatch(Constants.AUTHORITY, batchOps);
        batchOps.clear();
      }
      priority++;
    }
    if(batchOps.size() > 0){
      resolver.applyBatch(Constants.AUTHORITY, batchOps);
      batchOps.clear();
    }
    resolver.notifyChange(UDJEventProvider.PLAYLIST_URI, null, true);
  }

  private static Set<Long> getNeedUpdatePlaylistEntries(ContentResolver cr){
    HashSet<Long> toReturn = new HashSet<Long>();
    Cursor currentPlaylist = cr.query(
      UDJEventProvider.PLAYLIST_URI, 
      new String[]{UDJEventProvider.PLAYLIST_ID_COLUMN},
      null, null, null);
    if(currentPlaylist.moveToFirst()){
      int playlistIdColumn = 
        currentPlaylist.getColumnIndex(UDJEventProvider.PLAYLIST_ID_COLUMN);
      do{
        toReturn.add(currentPlaylist.getLong(playlistIdColumn));
      }while(currentPlaylist.moveToNext());
    }
    return toReturn;
  }


  private static void deleteRemovedPlaylistEntries(
    JSONArray playlistEntries, ContentResolver cr)
  {
    if(playlistEntries.length() ==0){
      return;
    }

    String where = "";
    String[] selectionArgs = new String[playlistEntries.size()];
    int i;
    for(i=0; i<playlistEntries.length()-1; i++){
      where += UDJEventProvider.PLAYLIST_ID_COLUMN + "!=? AND ";
      selectionArgs[i] = playlistEntries.getJSONObject(i).getString("id");
    }
    selectionArgs[i] = playlistEntries.getJSONObject(i).getString("id");
    where += UDJEventProvider.PLAYLIST_ID_COLUMN + "!=?";  

    cr.delete(UDJEventProvider.PLAYLIST_URI, where, selectionArgs); 
  }

  private static ContentProviderOperation getPlaylistInsertOp(
    JSONObject entry, int priority)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(UDJEventProvider.PLAYLIST_URI)
      .withValue(UDJEventProvider.PLAYLIST_ID_COLUMN, entry.getLong("id"))
      .withValue(UDJEventProvider.UP_VOTES_COLUMN, entry.getInt("up_votes"))
      .withValue(UDJEventProvider.DOWN_VOTES_COLUMN, entry.getInt("down_votes"))
      .withValue(UDJEventProvider.TIME_ADDED_COLUMN, 
        entry.getString("time_added"))
      .withValue(UDJEventProvider.PRIORITY_COLUMN, priority)
      .withValue(UDJEventProvider.TITLE_COLUMN, entry.getString("title"))
      .withValue(UDJEventProvider.ARTIST_COLUMN, entry.getString("artist"))
      .withValue(UDJEventProvider.ALBUM_COLUMN, entry.getString("album"))
      .withValue(UDJEventProvider.DURATION_COLUMN, entry.getInt("duration"))
      .withValue(UDJEventProvider.ADDER_ID_COLUMN, entry.getLong("adder_id"))
      .withValue(UDJEventProvider.ADDER_USERNAME_COLUMN, 
        entry.getString("adder_username"));
    return insertOp.build();
  }

  private static ContentProviderOperation getPlaylistPriorityUpdate(
    long id, int priority)
  {
    final ContentProviderOperation.Builder updateOp = 
      ContentProviderOperation.newUpdate(UDJEventProvider.PLAYLIST_URI)
      .withSelection(
        UDJEventProvider.PLAYLIST_ID_COLUMN + "=" + String.valueOf(id), null)
      .withValue(UDJEventProvider.PRIORITY_COLUMN, String.valueOf(priority));
    return updateOp.build();
  }

  public static void setPlaylistAddRequestsSynced(
    Set<Long> requestIds,
    Context context)
    throws RemoteException, OperationApplicationException
  {
    final ContentResolver resolver = context.getContentResolver();
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    for(Long requestId : requestIds){
      batchOps.add(getAddRequestSyncedOp(requestId));
      if(batchOps.size() >= 50){
        resolver.applyBatch(Constants.AUTHORITY, batchOps);
        batchOps.clear();
      }
    }
    if(batchOps.size() > 0){
      resolver.applyBatch(Constants.AUTHORITY, batchOps);
      batchOps.clear();
    }
  }
  
  private static ContentProviderOperation getAddRequestSyncedOp(long requestId){
    final ContentProviderOperation.Builder updateBuilder = 
      ContentProviderOperation.newUpdate(
        UDJEventProvider.PLAYLIST_ADD_REQUEST_URI)
      .withSelection(
        UDJEventProvider.ADD_REQUEST_ID_COLUMN + "=" +String.valueOf(requestId),
        null)
      .withValue(UDJEventProvider.ADD_REQUEST_SYNC_STATUS_COLUMN,
         UDJEventProvider.ADD_REQUEST_SYNCED);
    return updateBuilder.build();
  }

}
