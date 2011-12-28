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
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.network.ServerConnection;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;



public class RESTProcessor{

  public static final String TAG = "RESTProcessor";
  public static void setActivePlaylist(
    List<PlaylistEntry> playlistEntries,
    Context context)
    throws RemoteException, OperationApplicationException
  {
    final ContentResolver resolver = context.getContentResolver();
    deleteRemovedPlaylistEntries(playlistEntries, resolver);
    
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    Set<Long> needUpdate = 
      getNeedUpdatePlaylistEntries(playlistEntries, resolver);

    int priority = 1;
    for(PlaylistEntry pe: playlistEntries){
      if(needUpdate.contains(pe.getId())){
        batchOps.add(getPlaylistPriorityUpdate(pe.getId(), priority));
      }
      else{
        batchOps.add(getPlaylistInsertOp(pe, priority)); 
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

  private static Set<Long> getNeedUpdatePlaylistEntries(
    List<PlaylistEntry> playlistEntries, ContentResolver cr)
  {
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
    List<PlaylistEntry> playlistEntries, ContentResolver cr)
  {
    if(playlistEntries.size() ==0){
      return;
    }

    String where = "";
    String[] selectionArgs = new String[playlistEntries.size()];
    int i;
    for(i=0; i<playlistEntries.size()-1; i++){
      where += UDJEventProvider.PLAYLIST_ID_COLUMN + "!=? AND ";
      selectionArgs[i] = String.valueOf(playlistEntries.get(i).getId());
    }
    selectionArgs[i] = String.valueOf(playlistEntries.get(i).getId());
    where += UDJEventProvider.PLAYLIST_ID_COLUMN + "!=?";  

    cr.delete(UDJEventProvider.PLAYLIST_URI, where, selectionArgs); 
  }

  private static ContentProviderOperation getPlaylistInsertOp(
    PlaylistEntry pe, int priority)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(UDJEventProvider.PLAYLIST_URI)
      .withValue(UDJEventProvider.PLAYLIST_ID_COLUMN, pe.getId())
      .withValue(UDJEventProvider.UP_VOTES_COLUMN, pe.getUpVotes())
      .withValue(UDJEventProvider.DOWN_VOTES_COLUMN, pe.getDownVotes())
      .withValue(UDJEventProvider.TIME_ADDED_COLUMN, pe.getTimeAdded())
      .withValue(UDJEventProvider.PRIORITY_COLUMN, priority)
      .withValue(UDJEventProvider.TITLE_COLUMN, pe.getTitle())
      .withValue(UDJEventProvider.ARTIST_COLUMN, pe.getArtist())
      .withValue(UDJEventProvider.ALBUM_COLUMN, pe.getAlbum())
      .withValue(UDJEventProvider.DURATION_COLUMN, pe.getDuration())
      .withValue(UDJEventProvider.ADDER_ID_COLUMN, pe.getAdderId())
      .withValue(UDJEventProvider.ADDER_USERNAME_COLUMN, pe.getAdderUsername());
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
