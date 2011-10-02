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
import org.klnusbaum.udj.UDJPartyProvider;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.PartyActivity;
import org.klnusbaum.udj.network.ServerConnection;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;

public class RESTProcessor{

  public static void processPlaylistEntries(
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
    resolver.notifyChange(UDJPartyProvider.PLAYLIST_URI, null, true);
  }


  private static void insertPlaylistEntry(
    PlaylistEntry pe,
    ArrayList<ContentProviderOperation> batchOps)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(UDJPartyProvider.PLAYLIST_URI)
      .withValue(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, pe.getServerId())
      .withValue(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN, pe.getLibId())
      .withValue(UDJPartyProvider.TIME_ADDED_COLUMN, pe.getTimeAdded())
      .withValue(UDJPartyProvider.VOTES_COLUMN, pe.getVoteCount())
      .withValue(UDJPartyProvider.SONG_COLUMN, pe.getSong())
      .withValue(UDJPartyProvider.ARTIST_COLUMN, pe.getArtist())
      .withValue(UDJPartyProvider.ALBUM_COLUMN, pe.getAlbum())
      .withValue(UDJPartyProvider.PRIORITY_COLUMN, pe.getPriority())
      .withValue(UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.SYNCED_MARK);
    batchOps.add(insertOp.build());
  }

  private static void deletePlaylistEntry(
    PlaylistEntry pe,
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(pe.getServerId())};
    final ContentProviderOperation.Builder deleteOp = 
      ContentProviderOperation.newDelete(UDJPartyProvider.PLAYLIST_URI)
      .withSelection(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN + "=?", selectionArgs);
    batchOps.add(deleteOp.build());
  }
    
  private static void updatePlaylistEntry(
    PlaylistEntry pe, 
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(pe.getServerId())};
    final ContentProviderOperation.Builder updateBuilder = 
      ContentProviderOperation.newUpdate(UDJPartyProvider.PLAYLIST_URI)
      .withSelection(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN + "=?", selectionArgs)
      .withValue(UDJPartyProvider.VOTES_COLUMN, pe.getVoteCount())
      .withValue(UDJPartyProvider.PRIORITY_COLUMN, pe.getPriority())
      .withValue(UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.SYNCED_MARK);
    batchOps.add(updateBuilder.build());
  } 

  private static boolean 
    hasPlaylistEntry(PlaylistEntry pe, ContentResolver resolver)
  {
    if(
      pe.getClientId() == 
      Long.valueOf(UDJPartyProvider.INVALID_CLIENT_PLAYLIST_ID))
    {
      return false;
    }
    Cursor c = resolver.query(
      UDJPartyProvider.PLAYLIST_URI, 
      new String[] {"COUNT("+ UDJPartyProvider.PLAYLIST_ID_COLUMN+ ")"},
      UDJPartyProvider.PLAYLIST_ID_COLUMN+ "=?",
      new String[] {String.valueOf(pe.getClientId())},
      null);
    c.moveToNext();
    boolean toReturn = c.getInt(0) > 0;
    c.close();
    return toReturn;
  }

}
