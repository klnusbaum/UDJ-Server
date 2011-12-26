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

/*import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.UDJPartyProvider;
import org.klnusbaum.udj.R;
*/
import org.klnusbaum.udj.containers.PlaylistEntry;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class PlaylistSyncService extends IntentService{

  public static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
  public static final String EVENT_ID_EXTRA = "org.klnusbaum.udj.eventId";
  private static final String TAG = "PlyalistSyncService";
/*  public static final String LIB_ENTRY_EXTRA = "libEntry";
  public static final String PLAYLIST_ID_EXTRA = "playlistId";
  public static final String SEARCH_QUERY_EXTRA = "search_query";*/

  public PlaylistSyncService(){
    super("PlaylistSyncService");
  }

  @Override
  public void onHandleIntent(Intent intent){
    final Account account = (Account)intent.getParcelableExtra(ACCOUNT_EXTRA);
    long eventId = intent.getLongExtra(EVENT_ID_EXTRA, -1);
    //TODO hanle error if eventId or account aren't provided
    try{
      String authtoken = 
        AccountManager.get(this).blockingGetAuthToken(account, "", true);
      List<PlaylistEntry> newPlaylist =
        ServerConnection.getActivePlaylist(eventId, authtoken);
      RESTProcessor.setActivePlaylist(newPlaylist, this);
    }
    catch(JSONException e){
      Log.e(TAG, "JSON exception when retreiving playist");
    }
    catch(ParseException e){
      Log.e(TAG, "Parse exception when retreiving playist");
    }
    catch(IOException e){
      Log.e(TAG, "IO exception when retreiving playist");
    }
    catch(AuthenticationException e){
      Log.e(TAG, "Authentication exception when retreiving playist");
    }
    catch(AuthenticatorException e){
      Log.e(TAG, "Authentication exception when retreiving playist");
    }
    catch(OperationCanceledException e){
      Log.e(TAG, "Op Canceled exception when retreiving playist");
    }
    catch(RemoteException e){
      Log.e(TAG, "Remote exception when retreiving playist");
    }
    catch(OperationApplicationException e){
      Log.e(TAG, "Operation Application exception when retreiving playist");
    }
    //TODO This point of the app seems very dangerous as there are so many
    // exceptions that could occuer. Need to pay special attention to this.
  }

/*  private void updatePlaylist()
    throws JSONException, ParseException, IOException, AuthenticationException,
    RemoteException, OperationApplicationException
  {
    List<PlaylistEntry> serverResponse = 
      ServerConnection.getPlaylist(null);
    RESTProcessor.processPlaylistEntries(serverResponse, this);
  }

  private void addSongToPlaylist(LibraryEntry songToAdd)
    throws JSONException, ParseException, IOException, AuthenticationException
  {
    ContentValues toInsertValues = getPlaylistInsertionValues(songToAdd);
    Uri insertedSong = getContentResolver().insert(
      UDJPartyProvider.PLAYLIST_URI,
      toInsertValues);
    Cursor playlistSong = getPlaylistCursor(insertedSong);
    PlaylistEntry toSendToServer = PlaylistEntry.valueOf(playlistSong);
    List<PlaylistEntry> serverResponse =
      ServerConnection.addSongToPlaylist(toSendToServer, null);
    try{
      RESTProcessor.processPlaylistEntries(serverResponse, this);
    }
    catch(RemoteException e){

    }
    catch(OperationApplicationException e){

    }

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
  }*/
}
