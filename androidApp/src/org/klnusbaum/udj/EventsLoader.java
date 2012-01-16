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

package org.klnusbaum.udj;


import android.support.v4.content.AsyncTaskLoader;

import android.location.Location;
import android.util.Log;
import android.content.Context;
import android.accounts.OperationCanceledException;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.AuthenticatorException;

import java.io.IOException;
import java.io.FileOutputStream;
import java.util.List;

import org.apache.http.auth.AuthenticationException;

import org.json.JSONException;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.Event;

public class EventsLoader extends 
  AsyncTaskLoader<EventsLoader.EventsLoaderResult>
{
  public enum EventLoaderError{
    NO_ERROR, NO_CONNECTION, SERVER_ERROR, NO_LOCATION, 
    AUTHENTICATION_ERROR, NO_ACCOUNT};

  public static class EventsLoaderResult{
    private List<Event> events;
    private EventLoaderError error; 
    public EventsLoaderResult(List<Event> events, EventLoaderError error){
      this.events = events;
      this.error = error;
    }

    public EventLoaderError getError(){ 
      return error;
    }

    public List<Event> getEvents(){
      return events;
    }
  }

  private static final String TAG = "EVETNS_LOADER";

  private AccountManager am;
  private Account account;
  private Location location;
  private String searchQuery;
  private List<Event> events;
  private boolean locationSearch;

    
  public EventsLoader(Context context, Account account, Location location){
    super(context);
    am = AccountManager.get(context);
    this.account = account;
    this.location = location;
    this.events = null;
    this.searchQuery = null;
    locationSearch = true;
  }

  public EventsLoader(Context context, Account account, String query){
    super(context);
    am = AccountManager.get(context);
    this.account = account;
    this.location = null;
    this.events = null;
    this.searchQuery = query;
    locationSearch = false;
  }

  @Override
  protected void onStartLoading(){
    if(takeContentChanged() || events==null){
      forceLoad();
    }
  }
 
  public EventsLoaderResult loadInBackground(){
    if(account == null){
      return new EventsLoaderResult(null, EventLoaderError.NO_ACCOUNT);
    }
    else if(location == null && locationSearch){
      return new EventsLoaderResult(null, EventLoaderError.NO_LOCATION);
    }
    else if(!Utils.isNetworkAvailable(getContext())){
      return new EventsLoaderResult(null, EventLoaderError.NO_CONNECTION);
    }
    else{
      try{
        String authToken = am.blockingGetAuthToken(account, "", true); 
        if(locationSearch){
          Log.d(TAG, "Doing location search");
          return doLocationSearch(authToken);
        }
        else{
          Log.d(TAG, "Doing name search");
          return doNameSearch(authToken);
        }
      }
      catch(IOException e){
        Log.e(TAG, "IO exception");
      }
      catch(AuthenticatorException e){
        Log.e(TAG, "Authenticator exception");
        //TODO notify the user
      }
      catch(OperationCanceledException e){
        Log.e(TAG, "Operation cancelced exception");
        //TODO notify user
      }
      return new EventsLoaderResult(
        null, EventLoaderError.AUTHENTICATION_ERROR);
    }
  }
        
  private EventsLoaderResult doLocationSearch(String authToken){
    try{
      List<Event> events = 
        ServerConnection.getNearbyEvents(location, authToken);
      return new EventsLoaderResult(events, EventLoaderError.NO_ERROR);
    }
    catch(JSONException e){
      Log.e(TAG, "Json exception");
      Log.e(TAG, e.getMessage());
      //TODO notify the user
    }
    catch(IOException e){
      Log.e(TAG, "Io eception");
      //TODO notify the user
    }
    catch(AuthenticationException e){
      Log.e(TAG, "Authentication exception");
      //TODO notify the user
    }
    return new EventsLoaderResult(null, EventLoaderError.SERVER_ERROR);
  }

  private EventsLoaderResult doNameSearch(String authToken){
    try{
      List<Event> events = 
        ServerConnection.searchForEvents(searchQuery, authToken);
      return new EventsLoaderResult(events, EventLoaderError.NO_ERROR);
    }
    catch(JSONException e){
      Log.e(TAG, "Json exception");
      //TODO notify the user
    }
    catch(IOException e){
      Log.e(TAG, "Io eception");
      //TODO notify the user
    }
    catch(AuthenticationException e){
      Log.e(TAG, "Authentication exception");
      //TODO notify the user
    }
    return new EventsLoaderResult(null, EventLoaderError.SERVER_ERROR);
  }
}
