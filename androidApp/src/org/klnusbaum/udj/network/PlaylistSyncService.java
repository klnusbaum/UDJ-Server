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
import android.content.ContentResolver;
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
import android.app.PendingIntent;
import android.content.ContentValues;
import android.net.Uri;
import android.content.Intent;
import android.database.Cursor;
import android.app.Notification;
import android.app.NotificationManager;

import java.util.GregorianCalendar;
import java.util.List;
import java.io.IOException;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.HashMap;


import org.json.JSONObject;
import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.UDJEventProvider;
import org.klnusbaum.udj.EventActivity;
import org.klnusbaum.udj.EventSelectorActivity;
import org.klnusbaum.udj.R;
import org.klnusbaum.udj.exceptions.EventOverException;
import org.klnusbaum.udj.Utils;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class PlaylistSyncService extends IntentService{
  private static final int ADD_SONG_ID = 0;
  private static final int SONG_ADDED_ID = 1;

  private static final String TAG = "PlaylistSyncService";
  private static final String[] addRequestsProjection = new String[] {
    UDJEventProvider.ADD_REQUEST_ID_COLUMN,
    UDJEventProvider.ADD_REQUEST_LIB_ID_COLUMN};
  private static final String addRequestSeleciton = 
    UDJEventProvider.ADD_REQUEST_SYNC_STATUS_COLUMN + 
    "=" +
    UDJEventProvider.ADD_REQUEST_NEEDS_SYNC;

  public PlaylistSyncService(){
    super("PlaylistSyncService");
  }

  @Override
  public void onHandleIntent(Intent intent){
    Log.i(TAG, "In playlist sync service");
    final Account account = 
      (Account)intent.getParcelableExtra(Constants.ACCOUNT_EXTRA);
    long eventId = Long.valueOf(AccountManager.get(this).getUserData(
      account, Constants.LAST_EVENT_ID_DATA));
    //TODO hanle error if eventId is bad
    if(intent.getAction().equals(Intent.ACTION_INSERT)){
      if(intent.getData().equals(UDJEventProvider.PLAYLIST_ADD_REQUEST_URI)){
        long libId = intent.getLongExtra(
          Constants.LIB_ID_EXTRA, 
          UDJEventProvider.INVALID_LIB_ID);
        insertAddSongRequest(libId);
        syncAddRequests(account, eventId, true);
      }
      else if(intent.getData().equals(UDJEventProvider.VOTES_URI)){
        long playlistId = 
          intent.getLongExtra(Constants.PLAYLIST_ID_EXTRA, -1);
        int voteType = intent.getIntExtra(
          Constants.VOTE_TYPE_EXTRA, 
          UDJEventProvider.INVALID_VOTE_TYPE);
        addVoteRequest(playlistId, voteType);
        syncVoteRequests(account, eventId, true); 
      }
      updateActivePlaylist(account, eventId, true); 
    }
    else if(intent.getAction().equals(Intent.ACTION_VIEW)){
      updateActivePlaylist(account, eventId, true); 
    }
  }

  private void updateActivePlaylist(
    Account account, long eventId, boolean attemptReauth)
  {
    Log.d(TAG, "updating active playlist");
    AccountManager am = AccountManager.get(this);
    String authToken = "";
    try{
      authToken = am.blockingGetAuthToken(account, "", true);
    }
    catch(IOException e){
      Log.e(TAG, "IO exception when retreiving playist");
    }
    catch(OperationCanceledException e){
      Log.e(TAG, "Op Canceled exception when retreiving playist");
    }
    catch(AuthenticatorException e){
      Log.e(TAG, "Authentication exception when retreiving playist");
    }


    try{
      JSONObject activePlaylist =
        ServerConnection.getActivePlaylist(eventId, authToken);
      RESTProcessor.setActivePlaylist(activePlaylist, this);
    }
    catch(JSONException e){
      Log.e(TAG, "JSON exception when retreiving playist");
      Log.e(TAG, e.getMessage());
    }
    catch(ParseException e){
      Log.e(TAG, "Parse exception when retreiving playist");
    }
    catch(IOException e){
      Log.e(TAG, "IO exception when retreiving playist");
    }
    catch(AuthenticationException e){
      if(attemptReauth){
        Log.e(TAG, "Soft Authentication exception when retreiving playist");
        am.invalidateAuthToken(Constants.ACCOUNT_TYPE, authToken); 
        updateActivePlaylist(account, eventId, false);
      }
      else{
        Log.e(TAG, "Hard Authentication exception when retreiving playist");
      } 
    }
    catch(RemoteException e){
      Log.e(TAG, "Remote exception when retreiving playist");
    }
    catch(OperationApplicationException e){
      Log.e(TAG, "Operation Application exception when retreiving playist");
    }
    catch(EventOverException e){
      Log.e(TAG, "Event over exceptoin when retreiving playlist");
      Utils.handleEventOver(this, account);
    }
    //TODO This point of the app seems very dangerous as there are so many
    // exceptions that could occuer. Need to pay special attention to this.
  }

  private void syncAddRequests(
    Account account, long eventId, boolean attemptReauth)
  {
    Log.d(TAG, "Sycning add requests");
    ContentResolver cr = getContentResolver();
    Cursor requestsCursor = cr.query(
      UDJEventProvider.PLAYLIST_ADD_REQUEST_URI,
      addRequestsProjection,
      addRequestSeleciton,
      null,
      null);
    HashMap<Long, Long> addRequests = new HashMap<Long, Long>();
    if(requestsCursor.moveToFirst()){
      int requestIdColumn = requestsCursor.getColumnIndex(
        UDJEventProvider.ADD_REQUEST_ID_COLUMN);
      int libIdColumn = requestsCursor.getColumnIndex(
        UDJEventProvider.ADD_REQUEST_LIB_ID_COLUMN);
      do{
        addRequests.put(
          requestsCursor.getLong(requestIdColumn),
          requestsCursor.getLong(libIdColumn)); 
      }while(requestsCursor.moveToNext());
    }
    requestsCursor.close();

    if(addRequests.size() >0){
      String authToken = "";
      AccountManager am = AccountManager.get(this);
      try{
        authToken = am.blockingGetAuthToken(account, "", true);
      }
      catch(AuthenticatorException e){
        alertAddSongException(account);
        Log.e(TAG, "Authentication exception when adding to playist");
      }
      catch(OperationCanceledException e){
        alertAddSongException(account);
        Log.e(TAG, "Op Canceled exception when adding to playist");
      }
      catch(IOException e){
        alertAddSongException(account);
        Log.e(TAG, "IO exception when adding to playist");
      }

      try{
        ServerConnection.addSongsToActivePlaylist(
          addRequests, eventId, authToken);
        RESTProcessor.setPlaylistAddRequestsSynced(addRequests.keySet(), this);
      }
      catch(JSONException e){
        alertAddSongException(account);
        Log.e(TAG, "JSON exception when adding to playist");
      }
      catch(ParseException e){
        alertAddSongException(account);
        Log.e(TAG, "Parse exception when adding to playist");
      }
      catch(IOException e){
        alertAddSongException(account);
        Log.e(TAG, "IO exception when adding to playist");
      }
      catch(AuthenticationException e){
        if(attemptReauth){
          am.invalidateAuthToken(Constants.ACCOUNT_TYPE, authToken); 
          syncAddRequests(account, eventId, false);
          Log.e(TAG, "Soft Authentication exception when adding to playist");
        }
        else{
          alertAddSongException(account);
          Log.e(TAG, "Hard Authentication exception when adding to playist");
        }
      }
      catch(RemoteException e){
        alertAddSongException(account);
        Log.e(TAG, "Remote exception when adding to playist");
      }
      catch(OperationApplicationException e){
        alertAddSongException(account);
        Log.e(TAG, "Operation Application exception when adding to playist");
      }
      catch(EventOverException e){
        Log.e(TAG, "Event over exceptoin when retreiving playlist");
        Utils.handleEventOver(this, account);
      }
    }
    //TODO This point of the app seems very dangerous as there are so many
    // exceptions that could occuer. Need to pay special attention to this.
  }

  private void syncVoteRequests(
    Account account, long eventId, boolean attemptReauth)
  {
    Log.d(TAG, "Sycning vote requests");
    ContentResolver cr = getContentResolver();
    Cursor requestsCursor = cr.query(
      UDJEventProvider.VOTES_URI,
      null,
      UDJEventProvider.VOTE_SYNC_STATUS_COLUMN + "=" +
        UDJEventProvider.VOTE_NEEDS_SYNC,
      null,
      null);
    if(requestsCursor.getCount() >0){
      AccountManager am = AccountManager.get(this);
      String authToken = "";
      try{
        authToken = am.blockingGetAuthToken(account, "", true);
      }
      catch(IOException e){
        Log.e(TAG, "IO exception when retreiving playist");
      }
      catch(AuthenticatorException e){
        Log.e(TAG, "Authentication exception when retreiving playist");
      }
      catch(OperationCanceledException e){
        Log.e(TAG, "Op Canceled exception when retreiving playist");
      }

      try{
        Long userId = 
          Long.valueOf(am.getUserData(account, Constants.USER_ID_DATA));
        ServerConnection.doSongVotes(
          requestsCursor, eventId, userId, authToken);
        RESTProcessor.setVoteRequestsSynced(requestsCursor, this);
      }
      catch(ParseException e){
        Log.e(TAG, "Parse exception when retreiving playist");
      }
      catch(IOException e){
        Log.e(TAG, "IO exception when retreiving playist");
      }
      catch(AuthenticationException e){
        if(attemptReauth){
          Log.e(TAG, "Soft Authentication exception when retreiving playist");
          am.invalidateAuthToken(Constants.ACCOUNT_TYPE, authToken); 
          syncVoteRequests(account, eventId, false);
        }
        else{
          Log.e(TAG, "Hard Authentication exception when retreiving playist");
        }
      }
      catch(EventOverException e){
        Log.e(TAG, "Event over exceptoin when retreiving playlist");
        Utils.handleEventOver(this, account);
      }
      finally{
        requestsCursor.close();
      }
    }
      //TODO This point of the app seems very dangerous as there are so many
      // exceptions that could occuer. Need to pay special attention to this.
  }
  
  private void alertAddSongException(Account account){
    Notification addNotification = new Notification(
      R.drawable.udjlauncher, 
      getString(R.string.song_add_failed_title),
      System.currentTimeMillis());
    Intent syncVotes = new Intent(
      Intent.ACTION_INSERT,
      UDJEventProvider.PLAYLIST_ADD_REQUEST_URI,
      this,
      PlaylistSyncService.class);
    syncVotes.putExtra(Constants.ACCOUNT_EXTRA, account);
    PendingIntent pe = PendingIntent.getService(
      this, 0, syncVotes, 0);
    addNotification.setLatestEventInfo(
      this, 
      getString(R.string.song_add_failed_title),
      getString(R.string.song_add_failed_content),
      pe);
    addNotification.flags |= Notification.FLAG_AUTO_CANCEL;
    NotificationManager nm = 
      (NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
    nm.notify(SONG_ADDED_ID, addNotification);

  }

  private void addVoteRequest(long playlistId, int voteType){
    ContentResolver cr = getContentResolver();
    Cursor alreadyThere = cr.query(
      UDJEventProvider.VOTES_URI, 
      null,
      UDJEventProvider.VOTE_PLAYLIST_ENTRY_ID_COLUMN+"="+playlistId, 
      null, 
      null);
    if(alreadyThere.moveToFirst()){
      ContentValues toUpdate = new ContentValues();
      toUpdate.put(UDJEventProvider.VOTE_TYPE_COLUMN, voteType);
      toUpdate.put(UDJEventProvider.VOTE_SYNC_STATUS_COLUMN, 
        UDJEventProvider.VOTE_NEEDS_SYNC);
      cr.update(
        UDJEventProvider.VOTES_URI, 
        toUpdate, 
        UDJEventProvider.VOTE_PLAYLIST_ENTRY_ID_COLUMN+"="+playlistId, 
        null);
    }
    else{
      ContentValues toInsert = new ContentValues();
      toInsert.put(UDJEventProvider.VOTE_TYPE_COLUMN, voteType);
      toInsert.put(
        UDJEventProvider.VOTE_PLAYLIST_ENTRY_ID_COLUMN, 
        Long.valueOf(playlistId));
      cr.insert(UDJEventProvider.VOTES_URI, toInsert);
    }
    alreadyThere.close();
    showVoteToast(playlistId, voteType, cr);
  }

  private void showVoteToast(
    long playlistId, int voteType, ContentResolver cr)
  {
    Log.d(TAG, "Showing toast for id: " + String.valueOf(playlistId));
    String voteMessage = "";
    if(voteType == UDJEventProvider.UP_VOTE_TYPE){
      voteMessage += getString(R.string.voting_up_message);
    }
    else if(voteType == UDJEventProvider.DOWN_VOTE_TYPE){
      voteMessage += getString(R.string.voting_down_message);
    }
    Cursor song = cr.query(
      UDJEventProvider.PLAYLIST_URI, 
      new String[] {UDJEventProvider.TITLE_COLUMN},
      UDJEventProvider.PLAYLIST_ID_COLUMN + "=" + String.valueOf(playlistId),
      null,
      null);
    song.moveToFirst();
    Log.d(TAG, "number of values returned " + String.valueOf(song.getCount()));
    voteMessage += " " + song.getString(0);
    song.close();

    Intent showToast = new Intent(Constants.SHOW_TOAST_ACTION);
    showToast.putExtra(Intent.EXTRA_TEXT, voteMessage);
    sendBroadcast(showToast);
  }

  private void insertAddSongRequest(long libId){
    ContentValues toInsert = new ContentValues();
    toInsert.put(
      UDJEventProvider.ADD_REQUEST_LIB_ID_COLUMN, libId);
    ContentResolver cr = getContentResolver();
    cr.insert(
      UDJEventProvider.PLAYLIST_ADD_REQUEST_URI, 
      toInsert);
  }
}
