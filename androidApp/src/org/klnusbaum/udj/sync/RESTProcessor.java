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
  public static Thread libQuery(
    final String query, 
    final long partyId,
    final Handler messageHandler, 
    final Context context)
  {
    final Thread t = new Thread(){
      public void run(){
        doLibQuery(query, partyId,  messageHandler, context);
      }
    };
    t.start();
    return t;
  }

  private static void doLibQuery(
    final String query, 
    final long partyId,
    final Handler handler, 
    final Context context)
  {
    boolean success = true;
    try{
      List<LibraryEntry> searchResults =
        ServerConnection.libraryQuery(partyId, query);
      deleteAllLibEntries(context);
      Log.i("TAG", "did delete");
      processLibEntries(searchResults, context);
      Log.i("TAG", "processed lib");
    }
    catch(AuthenticationException e){
      Log.e("TAG", "Auth Exception");
      Log.e("TAG", e.getMessage());
      success = false;
    }
    catch(RemoteException e){
      Log.e("TAG", "Remote Exception");
      Log.e("TAG", e.getMessage());
      success = false;
    }
    catch(OperationApplicationException e){
      Log.e("TAG", "OperationApplicationException ");
      Log.e("TAG", e.getMessage());
      success = false;
    }
    catch(JSONException e){
      Log.e("TAG", "JSON Exception");
      Log.e("TAG", e.getMessage());
      success = false;
    }
    catch(IOException e){
      Log.e("TAG", "IO Exception");
      Log.e("TAG", e.getMessage());
      success = false;
    }
    final boolean finalSuccess = success;
    handler.post(new Runnable(){
      public void run(){
        ((PartyActivity)context).onSearchResult(finalSuccess);
      }
    });
  }

  public static void deleteAllLibEntries(Context context)
    throws RemoteException, OperationApplicationException
  {
    context.getContentResolver().delete(UDJPartyProvider.LIBRARY_URI,
      null, null);
  }

  public static void processLibEntries(
    List<LibraryEntry> newEntries, Context context)
    throws RemoteException, OperationApplicationException
  {
    final ContentResolver resolver = context.getContentResolver();
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    for(LibraryEntry le: newEntries){
      if(haveLibId(le.getServerId(), resolver)){
        if(le.getIsDeleted()){
          deleteLibraryEntry(le, batchOps);
        }
        else{
          updateLibraryEntry(le, batchOps);
        }
      } 
      else{
        insertLibraryEntry(le, batchOps); 
      }
      if(batchOps.size() >= 50){
        resolver.applyBatch(context.getString(R.string.authority), batchOps);
        batchOps.clear();
      }
    }
    if(batchOps.size() >= 0){
      resolver.applyBatch(context.getString(R.string.authority), batchOps);
      batchOps.clear();
    }
    resolver.notifyChange(UDJPartyProvider.LIBRARY_URI, null, true);
  }

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

  private static void deleteLibraryEntry(
    LibraryEntry le,
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(le.getServerId())};
    final ContentProviderOperation.Builder deleteOp = 
      ContentProviderOperation.newDelete(UDJPartyProvider.LIBRARY_URI)
      .withSelection(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN + "=?", selectionArgs);
    batchOps.add(deleteOp.build());
  }
    
  private static void updateLibraryEntry(
    LibraryEntry le, 
    ArrayList<ContentProviderOperation> batchOps)
  {
    String[] selectionArgs = new String[] {String.valueOf(le.getServerId())};
    final ContentProviderOperation.Builder updateBuilder = 
      ContentProviderOperation.newUpdate(UDJPartyProvider.LIBRARY_URI)
      .withSelection(UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN + "=?", selectionArgs)
      .withValue(UDJPartyProvider.SONG_COLUMN, le.getSong())
      .withValue(UDJPartyProvider.ARTIST_COLUMN, le.getArtist())
      .withValue(UDJPartyProvider.ALBUM_COLUMN, le.getAlbum());
    batchOps.add(updateBuilder.build());
  } 

  private static void insertLibraryEntry(
    LibraryEntry le,
    ArrayList<ContentProviderOperation> batchOps)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(UDJPartyProvider.LIBRARY_URI)
      .withValue(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN, le.getServerId())
      .withValue(UDJPartyProvider.SONG_COLUMN, le.getSong())
      .withValue(UDJPartyProvider.ARTIST_COLUMN, le.getArtist())
      .withValue(UDJPartyProvider.ALBUM_COLUMN, le.getAlbum());
    batchOps.add(insertOp.build());
  }


  private static boolean haveLibId(int serverLibId, ContentResolver resolver)
    throws OperationApplicationException
  {
    Cursor c = resolver.query(
      UDJPartyProvider.LIBRARY_URI, 
      new String[] {"COUNT("+ UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN+ ")"},
      UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN+ "=?",
      new String[] {String.valueOf(serverLibId)},
      null);
    c.moveToNext();
    boolean toReturn = c.getInt(0) > 0;
    c.close();
    return toReturn;
  }
}
