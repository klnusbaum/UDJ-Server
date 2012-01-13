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
import android.content.OperationApplicationException;
import android.util.Log;
import android.app.IntentService;
import android.content.Intent;

import java.io.IOException;
import java.util.HashMap;

import org.json.JSONException;
import org.json.JSONObject;

import org.apache.http.auth.AuthenticationException;

import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.Utils;
import org.klnusbaum.udj.UDJEventProvider;
import org.klnusbaum.udj.exceptions.EventOverException;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class EventCommService extends IntentService{

  public enum EventJoinError{
    NO_ERROR,
    AUTHENTICATION_ERROR,
    SERVER_ERROR,
    EVENT_OVER_ERROR,
    NO_NETWORK_ERROR 
  }

  private static final String TAG = "EventCommService";

  public EventCommService(){
    super("EventCommService");
  }

  @Override
  public void onHandleIntent(Intent intent){
    Log.d(TAG, "In Event Comm Service");
    AccountManager am = AccountManager.get(this);
    final Account account = 
      (Account)intent.getParcelableExtra(Constants.ACCOUNT_EXTRA);
    if(intent.getAction().equals(Intent.ACTION_INSERT)){
      enterEvent(intent, am, account);
    }
    else if(intent.getAction().equals(Intent.ACTION_DELETE)){
      //TODO handle if userId is null shouldn't ever be, but hey...
      leaveEvent(am, account);
    }
    else{
      Log.d(TAG, "ACTION wasn't delete or insert, it was " + 
        intent.getAction());
    } 
  }

  private void enterEvent(Intent intent, AccountManager am, Account account){
    am.setUserData(
      account, 
      Constants.EVENT_JOIN_ERROR, 
      String.valueOf(EventJoinError.NO_ERROR));

    if(!Utils.isNetworkAvailable(this)){
      doLoginFail(am, account, EventJoinError.NO_NETWORK_ERROR);
      return;
    }

    long userId, eventId;
    String authToken;
    //TODO hanle error if account isn't provided
    try{
      userId = 
        Long.valueOf(am.getUserData(account, Constants.USER_ID_DATA));
      //TODO handle if event id isn't provided
      authToken = am.blockingGetAuthToken(account, "", true);  
      eventId = intent.getLongExtra(
        Constants.EVENT_ID_EXTRA, 
        Constants.NO_EVENT_ID);
    }
    catch(OperationCanceledException e){
      Log.e(TAG, "Operation canceled exception in EventCommService" );
      doLoginFail(am, account, EventJoinError.AUTHENTICATION_ERROR);
      return;
    }
    catch(AuthenticatorException e){
      Log.e(TAG, "Authenticator exception in EventCommService" );
      doLoginFail(am, account, EventJoinError.AUTHENTICATION_ERROR);
      return;
    }
    catch(IOException e){
      Log.e(TAG, "IO exception in EventCommService" );
      doLoginFail(am, account, EventJoinError.AUTHENTICATION_ERROR);
      return;
    }

    try{
      ServerConnection.joinEvent(eventId, userId, authToken);
      ContentResolver cr = getContentResolver();
      UDJEventProvider.eventCleanup(cr);          
      HashMap<Long,Long> previousRequests = ServerConnection.getAddRequests(
        userId, eventId, authToken);
      UDJEventProvider.setPreviousAddRequests(cr, previousRequests);
      JSONObject previousVotes = 
        ServerConnection.getVoteRequests(userId, eventId, authToken);
      UDJEventProvider.setPreviousVoteRequests(cr, previousVotes);
      Intent joinedEventIntent = new Intent(Constants.JOINED_EVENT_ACTION);
      am.setUserData(
        account, Constants.LAST_EVENT_ID_DATA, String.valueOf(eventId));
      am.setUserData(
        account, Constants.IN_EVENT_DATA, 
        String.valueOf(Constants.IN_EVENT_FLAG));
      sendBroadcast(joinedEventIntent);
      return;
    }
    catch(IOException e){
      Log.e(TAG, "IO exception when joining event");
      Log.e(TAG, e.getMessage());
      doLoginFail(am, account, EventJoinError.SERVER_ERROR);
    }
    catch(JSONException e){
      Log.e(TAG, 
        "JSON exception when joining event");
      Log.e(TAG, e.getMessage());
      doLoginFail(am, account, EventJoinError.SERVER_ERROR);
    }
    catch(AuthenticationException e){
      Log.e(TAG, 
        "Authentication exception when joining event");
      Log.e(TAG, e.getMessage());
      doLoginFail(am, account, EventJoinError.AUTHENTICATION_ERROR);
    }
    catch(EventOverException e){
      Log.e(TAG, "Event Over Exception when joining event");
      Log.e(TAG, e.getMessage());
      doLoginFail(am, account, EventJoinError.EVENT_OVER_ERROR);
    }
  }

  private void doLoginFail(
    AccountManager am, 
    Account account, 
    EventJoinError error)
  {
    am.setUserData(
      account, 
      Constants.EVENT_JOIN_ERROR, 
      error.toString());
    Intent eventJoinFailedIntent = 
      new Intent(Constants.EVENT_JOIN_FAILED_ACTION);
    Log.d(TAG, "Sending event join failure broadcast");
    sendBroadcast(eventJoinFailedIntent);
  }

  private void leaveEvent(AccountManager am, Account account){
    Log.d(TAG, "In leave event"); 
    
    if(account == null){
      //TODO handle error
      return;
    }

    long userId;
    String authToken; 
    try{
      userId = 
        Long.valueOf(am.getUserData(account, Constants.USER_ID_DATA));
      //TODO handle if event id isn't provided
      authToken = am.blockingGetAuthToken(account, "", true);  
    }
    catch(OperationCanceledException e){
      Log.e(TAG, "Operation canceled exception in EventCommService" );
      return;
    }
    catch(AuthenticatorException e){
      Log.e(TAG, "Authenticator exception in EventCommService" );
      return;
    }
    catch(IOException e){
      Log.e(TAG, "IO exception in EventCommService" );
      return;
    }

    try{
      long eventId = 
        Long.valueOf(am.getUserData(account, Constants.LAST_EVENT_ID_DATA));
      if(eventId != Constants.NO_EVENT_ID){
        ServerConnection.leaveEvent(eventId, Long.valueOf(userId), authToken);
        setNotInEvent(account);
        Intent leftEventIntent = new Intent(Constants.LEFT_EVENT_ACTION);
        sendBroadcast(leftEventIntent);
      }
    }
    catch(IOException e){
      Log.e(TAG, "IO exception in EventCommService: " + e.getMessage());
    }
    catch(AuthenticationException e){
      Log.e(TAG, "Authentication exception in EventCommService" );
    }
    //TODO need to implement exponential back off when log out fails.
    // 1. This is just nice to the server
    // 2. If we don't log out, there could be problems on the next event joined
  }

  private void setNotInEvent(Account account){
    AccountManager am = AccountManager.get(this);
    am.setUserData(account, Constants.LAST_EVENT_ID_DATA, 
      String.valueOf(Constants.NO_EVENT_ID));
    am.setUserData(account, Constants.IN_EVENT_DATA, 
      String.valueOf(Constants.NOT_IN_EVENT_FLAG));
  }

}
