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

import org.klnusbaum.udj.Constants;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class EventCommService extends IntentService{

  private static final String TAG = "EventCommService";

  public EventCommService(){
    super("EventCommService");
  }

  @Override
  public void onHandleIntent(Intent intent){
    Log.d(TAG, "In Event Comm Service");
    final Account account = 
      (Account)intent.getParcelableExtra(Constants.ACCOUNT_EXTRA);
    //TODO hanle error if account isn't provided
    long eventId = 
      intent.getLongExtra(Constants.EVENT_ID_EXTRA, Constants.NO_EVENT_ID);
    //TODO handle if event id isn't provided
    if(intent.getAction().equals(Intent.ACTION_INSERT)){
      enterEvent(account, intent);
    }
    else if(intent.getAction().equals(Intent.ACTION_DELETE)){
      leaveEvent(account, intent);
    }
    else{
      Log.d(TAG, "ACTION wasn't delete or insert, it was " + 
        intent.getAction());
    } 
  }

  private void enterEvent(Account account, long eventId){
    try{
      AccountManager am = AccountManager.get(this);
      String authToken = am.blockingGetAuthToken(account, "", true);  
      long userId = 
        Long.valueOf(am.getUserData(account, Constants.USER_ID_DATA));
      if(ServerConnection.joinEvent(eventId, userId, authToken)){
        UDJEventProvider.eventCleanup(cr);          
        HashMap<Long,Long> previousRequests = ServerConnection.getAddRequests(
          userId, params[0], authToken);
        UDJEventProvider.setPreviousAddRequests(cr, previousRequests);
        JSONObject previousVotes = 
          ServerConnection.getVoteRequests(userId, params[0], authToken);
        UDJEventProvider.setPreviousVoteRequests(cr, previousVotes);
        Intent joinedEventIntent = new Intent(Contants.JOINED_EVENT_ACTION);
        sendBroadcast(joinedEventIntent);
        return;
      }
      else{
        Intent eventJoinFailedIntent = 
          new Intent(Contants.EVENT_JOIN_FAILED_ACTION);
        sendBroadcast(eventJoinFailedIntent);
        return;
      }
    }
    catch(IOException e){
      Log.e(EVENT_LOGIN_TAG, "IO exception when logging in" + e.getMessage());
      //TODO notify the user
    }
    catch(AuthenticatorException e){
      Log.e(EVENT_LOGIN_TAG, 
        "Authentiator exception when logging in" + e.getMessage());
      //TODO notify the user
    }
    catch(OperationCanceledException e){
      Log.e(EVENT_LOGIN_TAG, 
        "Op cancled exception when logging in" + e.getMessage());
        //TODO notify user
    }
    catch(JSONException e){
      Log.e(EVENT_LOGIN_TAG, 
        "JSON exception when logging in" + e.getMessage());
      //TODO notify user
    }
    catch(AuthenticationException e){
      Log.e(EVENT_LOGIN_TAG, 
        "Authentication exception when logging in" + e.getMessage());
      //TODO notify user
    }
    //Inform user loggning in was unsuccesuf
    Intent eventJoinFailedIntent = 
      new Intent(Contants.EVENT_JOIN_FAILED_ACTION);
    sendBroadcast(eventJoinFailedIntent);
  }

  private void leaveEvent(Account account, long eventId){
    Log.d(TAG, "In leave event"); 
    String authToken = null;
    AccountManager am = AccountManager.get(this);
    try{
      authToken = am.get(this).blockingGetAuthToken(account, "", true);
      String userId = AccountManager.get(this).getUserData(
        account, Constants.USER_ID_DATA);
      //TODO handle if userId is null shouldn't ever be, but hey...
      ServerConnection.leaveEvent(eventId, Long.valueOf(userId), authToken);
      am.setUserData(account, Constants.EVENT_ID_EXTRA, Constants.NO_EVENT_ID);
      Intent leftEventIntent = new Intent(Contants.LEFT_EVENT_ACTION);
      sendBroadcast(leftEventIntent);
    }
    catch(IOException e){
      Log.e(TAG, "IO exception in EventCommService: " + e.getMessage());
    }
    catch(AuthenticationException e){
      Log.e(TAG, "Authentication exception in EventCommService" );
    }
    catch(OperationCanceledException e){
      Log.e(TAG, "Operation canceled exception in EventCommService" );
    }
    catch(AuthenticatorException e){
      Log.e(TAG, "Operation canceled exception in EventCommService" );
    }
  }
}
