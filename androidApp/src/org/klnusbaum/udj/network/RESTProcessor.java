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

import android.content.Context;
import android.content.ContentResolver;
import android.content.ContentProviderOperation;
import android.content.OperationApplicationException;
import android.database.Cursor;
import android.os.RemoteException;
import android.util.Log;
import android.os.Handler;

import org.klnusbaum.udj.R;
import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.UDJEventProvider;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.network.ServerConnection;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;

public class RESTProcessor{

  public static void setActivePlaylist(
    List<PlaylistEntry> playlistEntries,
    Context context)
    throws RemoteException, OperationApplicationException
  {
    final ContentResolver resolver = context.getContentResolver();
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    final ContentProviderOperation.Builder deleteOp = 
      ContentProviderOperation.newDelete(UDJEventProvider.PLAYLIST_URI);
    batchOps.add(deleteOp.build());
    int priority = 1;
    for(PlaylistEntry pe: playlistEntries){
      batchOps.add(getPlaylistInsertOp(pe, priority));
      ++priority;
      if(batchOps.size() >= 50){
        resolver.applyBatch(Constants.AUTHORITY, batchOps);
      }
    }
    if(batchOps.size() > 0){
      resolver.applyBatch(Constants.AUTHORITY, batchOps);
      batchOps.clear();
    }
    resolver.notifyChange(UDJEventProvider.PLAYLIST_URI, null, true);
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
      .withValue(UDJEventProvider.SONG_COLUMN, pe.getSong())
      .withValue(UDJEventProvider.ARTIST_COLUMN, pe.getArtist())
      .withValue(UDJEventProvider.ALBUM_COLUMN, pe.getAlbum())
      .withValue(UDJEventProvider.DURATION_COLUMN, pe.getDuration())
      .withValue(UDJEventProvider.ADDER_ID_COLUMN, pe.getAdderId())
      .withValue(UDJEventProvider.ADDER_USERNAME_COLUMN, pe.getAdderUsername());
    return insertOp.build();
  }

  /*public static void processPlaylistEntries(
    List<PlaylistEntry> newEntries, Context context)
    throws RemoteException, OperationApplicationException
  {
    Log.i("TAG", "Processing " + String.valueOf(newEntries.size()) 
    + " entries");
    final ContentResolver resolver = context.getContentResolver();
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    for(PlaylistEntry pe: newEntries){
      if(pe.getIsDeleted()){
        deletePlaylistEntry(pe, batchOps);
      }
      else if(hasPlaylistEntry(pe, resolver)){
        updatePlaylistEntry(pe, batchOps);
      }
      else{
        insertPlaylistEntry(pe, batchOps);
      }

      if(batchOps.size() >= 50){
        resolver.applyBatch(context.getString(R.string.authority), batchOps);
        batchOps.clear();
      }
    }  
    if(batchOps.size() > 0){
      resolver.applyBatch(context.getString(R.string.authority), batchOps);
      batchOps.clear();
    }
    resolver.notifyChange(UDJEventProvider.PLAYLIST_URI, null, true);
  }


  private static void insertPlaylistEntry(
    PlaylistEntry pe,
    ArrayList<ContentProviderOperation> batchOps)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(UDJEventProvider.PLAYLIST_URI)
      .withValue(UDJEventProvider.SERVER_PLAYLIST_ID_COLUMN, pe.getServerId())
      .withValue(UDJEventProvider.SERVER_LIBRARY_ID_COLUMN, pe.getLibId())
      .withValue(UDJEventProvider.TIME_ADDED_COLUMN, pe.getTimeAdded())
      .withValue(UDJEventProvider.VOTES_COLUMN, pe.getVoteCount())
      .withValue(UDJEventProvider.SONG_COLUMN, pe.getSong())
      .withValue(UDJEventProvider.ARTIST_COLUMN, pe.getArtist())
      .withValue(UDJEventProvider.ALBUM_COLUMN, pe.getAlbum())
      .withValue(UDJEventProvider.PRIORITY_COLUMN, pe.getPriority())
      .withValue(UDJEventProvider.SYNC_STATE_COLUMN, UDJEventProvider.SYNCED_MARK);
    batchOps.add(insertOp.build());
  }

  private static void deletePlaylistEntry(
    PlaylistEntry pe,
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(pe.getServerId())};
    final ContentProviderOperation.Builder deleteOp = 
      ContentProviderOperation.newDelete(UDJEventProvider.PLAYLIST_URI)
      .withSelection(UDJEventProvider.SERVER_PLAYLIST_ID_COLUMN + "=?", selectionArgs);
    batchOps.add(deleteOp.build());
  }
    
  private static void updatePlaylistEntry(
    PlaylistEntry pe, 
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(pe.getServerId())};
    final ContentProviderOperation.Builder updateBuilder = 
      ContentProviderOperation.newUpdate(UDJEventProvider.PLAYLIST_URI)
      .withSelection(UDJEventProvider.SERVER_PLAYLIST_ID_COLUMN + "=?", selectionArgs)
      .withValue(UDJEventProvider.VOTES_COLUMN, pe.getVoteCount())
      .withValue(UDJEventProvider.PRIORITY_COLUMN, pe.getPriority())
      .withValue(UDJEventProvider.SYNC_STATE_COLUMN, UDJEventProvider.SYNCED_MARK);
    batchOps.add(updateBuilder.build());
  } 

  private static boolean 
    hasPlaylistEntry(PlaylistEntry pe, ContentResolver resolver)
  {
    if(
      pe.getClientId() == 
      Long.valueOf(UDJEventProvider.INVALID_CLIENT_PLAYLIST_ID))
    {
      return false;
    }
    Cursor c = resolver.query(
      UDJEventProvider.PLAYLIST_URI, 
      new String[] {"COUNT("+ UDJEventProvider.PLAYLIST_ID_COLUMN+ ")"},
      UDJEventProvider.PLAYLIST_ID_COLUMN+ "=?",
      new String[] {String.valueOf(pe.getClientId())},
      null);
    c.moveToNext();
    boolean toReturn = c.getInt(0) > 0;
    c.close();
    return toReturn;
  }
*/
}
