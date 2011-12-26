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

  public static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
  public static final String EVENT_ID_EXTRA = "org.klnusbaum.udj.eventId";
  private static final String TAG = "EventCommService";
/*  public static final String LIB_ENTRY_EXTRA = "libEntry";
  public static final String PLAYLIST_ID_EXTRA = "playlistId";
  public static final String SEARCH_QUERY_EXTRA = "search_query";*/

  public EventCommService(){
    super("EventCommService");
  }

  @Override
  public void onHandleIntent(Intent intent){
    Log.d(TAG, "In Event Comm Service");
    final Account account = (Account)intent.getParcelableExtra(ACCOUNT_EXTRA);
    //TODO hanle error if account isn't provided
    if(intent.getAction().equals(Intent.ACTION_DELETE)){
      leaveEvent(account, intent);
    }
    else{
      Log.d(TAG, "ACTION wasn't delete, it was " + intent.getAction());
    } 
  }

  private void leaveEvent(Account account, Intent intent){
    Log.d(TAG, "In leave event"); 
    String authtoken = null;
    try{
      authtoken = 
        AccountManager.get(this).blockingGetAuthToken(account, "", true);
      long eventId = intent.getLongExtra(EVENT_ID_EXTRA, -1);
      //TODO handle if event id isn't provided
      String userId = AccountManager.get(this).getUserData(
        account, Constants.USER_ID_DATA);
      //TODO handle if userId is null shouldn't ever be, but hey...
      ServerConnection.leaveEvent(eventId, Long.valueOf(userId), authtoken);
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
