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
import android.content.ContentValues;
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

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;



public class RESTProcessor{

  public static final String TAG = "RESTProcessor";

  private static void setCurrentSong(JSONObject currentSong, ContentResolver cr)
    throws JSONException
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
    cr.notifyChange(UDJEventProvider.CURRENT_SONG_URI, null);
  }

  public static void setActivePlaylist(
    JSONObject activePlaylist,
    Context context)
    throws RemoteException, OperationApplicationException, JSONException
  {
    JSONArray playlistEntries = activePlaylist.getJSONArray("active_playlist");
    JSONObject currentSong = activePlaylist.getJSONObject("current_song");
    final ContentResolver resolver = context.getContentResolver();

    if(currentSong.length() > 0){
      setCurrentSong(currentSong, resolver);
    }

    deleteRemovedPlaylistEntries(playlistEntries, resolver);
    
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    Set<Long> needUpdate = getNeedUpdatePlaylistEntries(resolver);

    int priority = 1;
    JSONObject currentEntry;
    for(int i=0; i<playlistEntries.length(); i++){
      currentEntry = playlistEntries.getJSONObject(i);
      long id = currentEntry.getLong("id");
      if(needUpdate.contains(id)){
        batchOps.add(getPlaylistPriorityUpdate(currentEntry, priority));
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
    resolver.notifyChange(UDJEventProvider.PLAYLIST_URI, null);
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
    currentPlaylist.close();
    return toReturn;
  }


  private static void deleteRemovedPlaylistEntries(
    JSONArray playlistEntries, ContentResolver cr)
    throws JSONException
  {
    if(playlistEntries.length() ==0){
      return;
    }

    String where = "";
    String[] selectionArgs = new String[playlistEntries.length()];
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
    throws JSONException
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
    JSONObject currentEntry, int priority)
    throws JSONException
  {
    final ContentProviderOperation.Builder updateOp = 
      ContentProviderOperation.newUpdate(UDJEventProvider.PLAYLIST_URI)
      .withSelection(
        UDJEventProvider.PLAYLIST_ID_COLUMN + 
        "=" + currentEntry.getInt("id"), null)
      .withValue(UDJEventProvider.PRIORITY_COLUMN, String.valueOf(priority))
      .withValue(
        UDJEventProvider.UP_VOTES_COLUMN, currentEntry.getInt("up_votes"))
      .withValue(
        UDJEventProvider.DOWN_VOTES_COLUMN, currentEntry.getInt("down_votes"));
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

  public static void setVoteRequestsSynced(Cursor voteRequests, Context context)
  {
    ContentResolver cr = context.getContentResolver();
    if(voteRequests.moveToFirst()){
      int idColIndex = 
        voteRequests.getColumnIndex(UDJEventProvider.VOTE_ID_COLUMN);
      do{
        //TODO these should be batch operations
        long requestId = voteRequests.getLong(idColIndex);
        ContentValues updatedValue = new ContentValues();
        updatedValue.put(
          UDJEventProvider.VOTE_SYNC_STATUS_COLUMN, 
          UDJEventProvider.VOTE_SYNCED);
        cr.update(
          UDJEventProvider.VOTES_URI,
          updatedValue,
          UDJEventProvider.VOTE_ID_COLUMN + "=" + requestId,
          null);
      }while(voteRequests.moveToNext());
    }
  }

}
