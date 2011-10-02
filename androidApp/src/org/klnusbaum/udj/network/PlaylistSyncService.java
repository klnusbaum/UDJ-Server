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


import android.content.AbstractThreadedSyncAdapter;
import android.content.SyncResult;
import android.content.Context;
import android.os.Bundle;
import android.content.ContentProviderClient;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.OperationCanceledException;
import android.accounts.AuthenticatorException;
import android.database.Cursor;
import android.os.RemoteException;
import android.content.OperationApplicationException;
import android.util.Log;
import android.app.IntentService;

import java.util.GregorianCalendar;
import java.util.List;
import java.io.IOException;
import java.util.ArrayList;
import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.Party;
import org.klnusbaum.udj.UDJPartyProvider;
import org.klnusbaum.udj.R;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class PlaylistSyncService extends IntentService{
  private GregorianCalendar playlistLastUpdate;

  private AccountManager am;

  public static final String ACCOUNT_EXTRA = "account";
  public static final String LIB_ID_EXTRA = "libId";
  public static final String PLAYLIST_ID_EXTRA = "playlistId";
  public static final String SEARCH_QUERY_EXTRA = "search_query";


  /*private static final String[] playlistProjection = new String[]{
    UDJPartyProvider.PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SYNC_STATE_COLUMN};*/
  private static final String playlistWhereClause = 
    UDJPartyProvider.SYNC_STATE_COLUMN + "=?";

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
        long toAdd = intent.getLongExtra(
          LIB_ID_EXTRA, LibraryEntry.INVALID_SERVER_LIB_ID);  
        addSongToPlaylist(toAdd);
      }
      else if(action.equals(Intent.ACTION_VIEW)){
        updatePlaylist();
      }
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
        account, context.getString(R.string.authtoken_type), true);
      if(authtoken == null){
        //TODO throw exeception if authtoken is null
      }
      am.invalidateAuthToken(
        context.getString(R.string.account_type), authtoken);
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
      ServerConnection.getPlaylist();
    RESTProcessor.processPlaylistEntries(serverResponse);
  }

  private void addSongToPlaylist(long libId){
    Cursor songToAdd = getLibraryCursor(libId);
    ContentValues toInsertValues = getPlaylistInsertionValues(songToAdd);
    Uri insertedSong = getContentResolver().insert(
      UDJPartyProvider.PLAYLIST_URI,
      toInsertValues);
    Cursor playlistSong = getPlaylistCursor(insertedSong);
    PlaylistEntry toSendToServer = PlaylistEntry.valueOf(playlistSong);
    List<PlaylistEntry> serverResponse =
      ServerConnection.addSongToPlaylist(toSendToServer);
    RESTProcessor.processPlaylistEntries(serverResponse);
  }

  private ContentValues getPlaylistInsertionValues(Cursor libraryCursor){
    ContentValues toInsertValues = new ContentValues();
    toInsertValues.put(SERVER_LIBRARY_ID_COLUMN, libraryCursor.getLong(
      libraryCursor.getColumnIndex(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN)));
    toInsertValues.put(SONG_COLUMN, libraryCursor.getString(
      libraryCursor.getColumnIndex(UDJPartyProvider.SONG_COLUMN)));
    toInsertValues.put(ALBUM_COLUMN, libraryCursor.getString(
      libraryCursor.getColumnIndex(UDJPartyProvider.ALBUM_COLUMN)));
    toInsertValues.put(ARTIST_COLUMN, libraryCursor.getString(
      libraryCursor.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)));
    return toInsertValues;
  }

  private Cursor getLibraryCursor(long libId){
    if(libId == LibraryEntry.INVALID_SERVER_LIB_ID){
      //TODO throw some sort of error
    }
    Cursor librarySong = getContentResolver().query(
      LIBRARY_URI,
      null, 
      SERVER_LIBRARY_ID_COLUMN + " = ?",
      new String[]{String.valueOf(libId)}, 
      null);
    if(librarySong.getCount() == 0){
      //TODO throw some sort of error
    }
    librarySong.moveToNext();
    return librarySong;
  }

  private Cursor getPlaylistCursor(Uri songUri){
    String playlistId = songUri.getLastPathSegment();
    Cursor playlistSong = getContentResolver().query(
      PLAYLIST_URI,
      null,
      PLAYLIST_ID_COLUMN + " = ? ",
      new String[]{playlistId},
      null);
    if(playlistSong.getCount() == 0){
      //TODO throw some kind of error
    }
    playlistSong.moveToNext();
    return playlistSong;
  }
}
