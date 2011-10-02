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


import android.content.Context;
import android.os.Bundle;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.OperationCanceledException;
import android.accounts.AuthenticatorException;
import android.database.Cursor;
import android.os.RemoteException;
import android.content.OperationApplicationException;
import android.util.Log;
import android.app.IntentService;
import android.content.ContentValues;
import android.net.Uri;
import android.content.Intent;

import java.util.GregorianCalendar;
import java.util.List;
import java.io.IOException;
import java.util.ArrayList;
import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.UDJPartyProvider;
import org.klnusbaum.udj.R;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class PlaylistSyncService extends IntentService{
  private GregorianCalendar playlistLastUpdate;

  private AccountManager am;

  public static final String ACCOUNT_EXTRA = "account";
  public static final String LIB_ENTRY_EXTRA = "libEntry";
  public static final String PLAYLIST_ID_EXTRA = "playlistId";
  public static final String SEARCH_QUERY_EXTRA = "search_query";


  /*private static final String[] playlistProjection = new String[]{
    UDJPartyProvider.PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SYNC_STATE_COLUMN};*/
  private static final String playlistWhereClause = 
    UDJPartyProvider.SYNC_STATE_COLUMN + "=?";

  public PlaylistSyncService(String name){
    super(name);
  }

  @Override
  public void onCreate(){
    super.onCreate();
    am = AccountManager.get(this);
  }

  @Override
  public void onHandleIntent(Intent intent){
    final Account account = (Account)intent.getParcelableExtra(ACCOUNT_EXTRA);
    String authtoken = null;
    String action = intent.getAction();
    try{
      if(action.equals(Intent.ACTION_INSERT)){
        Bundle libEntryBundle = intent.getBundleExtra(
          LIB_ENTRY_EXTRA);  
        if(libEntryBundle == null){
          //TODO throw error
        }
        addSongToPlaylist(LibraryEntry.fromBundle(libEntryBundle));
      }
      else if(action.equals(Intent.ACTION_VIEW)){
        updatePlaylist();
      }
      playlistLastUpdate = new GregorianCalendar(); 
      //TODO something in the case of these failing.
    } 
    catch(final AuthenticatorException e){

    } 
    catch(final OperationCanceledException e){

    }
    catch(final IOException e){

    }
    catch(final AuthenticationException e){
      authtoken = am.blockingGetAuthToken(
        account, getString(R.string.authtoken_type), true);
      if(authtoken == null){
        //TODO throw exeception if authtoken is null
      }
      am.invalidateAuthToken(
        getString(R.string.account_type), authtoken);
    }
    catch(final ParseException e){
    
    }
    catch(final JSONException e){
      Log.e("TAG", "JSON EXception!!!!");
      Log.e("TAG", e.getMessage());
    }
    catch(final RemoteException e){

    }
    catch(final OperationApplicationException e){

    }
  }

  private void updatePlaylist(){
    List<PlaylistEntry> serverResponse = 
      ServerConnection.getPlaylist(playlistLastUpdate);
    RESTProcessor.processPlaylistEntries(serverResponse, this);
  }

  private void addSongToPlaylist(LibraryEntry songToAdd){
    ContentValues toInsertValues = getPlaylistInsertionValues(songToAdd);
    Uri insertedSong = getContentResolver().insert(
      UDJPartyProvider.PLAYLIST_URI,
      toInsertValues);
    Cursor playlistSong = getPlaylistCursor(insertedSong);
    PlaylistEntry toSendToServer = PlaylistEntry.valueOf(playlistSong);
    List<PlaylistEntry> serverResponse =
      ServerConnection.addSongToPlaylist(toSendToServer, playlistLastUpdate);
    RESTProcessor.processPlaylistEntries(serverResponse, this);
  }

  private ContentValues getPlaylistInsertionValues(LibraryEntry songToAdd){
    ContentValues toInsertValues = new ContentValues();
    toInsertValues.put(
      UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN, 
      songToAdd.getServerId());
    toInsertValues.put(
      UDJPartyProvider.SONG_COLUMN,
      songToAdd.getSong());
    toInsertValues.put(
      UDJPartyProvider.ARTIST_COLUMN,
      songToAdd.getArtist());
    toInsertValues.put(
      UDJPartyProvider.ALBUM_COLUMN,
      songToAdd.getAlbum());
    return toInsertValues;
  }

  private Cursor getPlaylistCursor(Uri songUri){
    String playlistId = songUri.getLastPathSegment();
    Cursor playlistSong = getContentResolver().query(
      UDJPartyProvider.PLAYLIST_URI,
      null,
      UDJPartyProvider.PLAYLIST_ID_COLUMN + " = ? ",
      new String[]{playlistId},
      null);
    if(playlistSong.getCount() == 0){
      //TODO throw some kind of error
    }
    playlistSong.moveToNext();
    return playlistSong;
  }
}
