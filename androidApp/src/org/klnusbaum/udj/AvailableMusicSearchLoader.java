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

import android.content.Context;
import android.util.Log;
import android.accounts.OperationCanceledException;
import android.accounts.AuthenticatorException;
import android.accounts.AccountManager;
import android.accounts.Account;

import java.util.List;
import java.io.IOException;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.LibraryEntry;

public class AvailableMusicSearchLoader 
  extends AsyncTaskLoader<List<LibraryEntry>>
{
  private String query;
  private long eventId;
  private Account account;

  public AvailableMusicSearchLoader(
    Context context, String query, long eventId,  Account account)
  {
    super(context);
    this.query = query;
    this.eventId = eventId;
    this.account = account;
  }

  public List<LibraryEntry> loadInBackground(){
    if(query != null){
      try{
        String authToken = AccountManager.get(getContext()).
          blockingGetAuthToken(account, "", true);
        return ServerConnection.availableMusicQuery(query, eventId, authToken);
        //TODO do something to the potential errors
      }
      catch(JSONException e){

      }
      catch(ParseException e){

      }
      catch(IOException e){

      }
      catch(AuthenticationException e){

      }
      catch(AuthenticatorException e){
        //TODO notify the user
      }
      catch(OperationCanceledException e){
        //TODO notify user
      }
      return null;
    }
    return null;
  }

  @Override
  protected void onStartLoading(){
    forceLoad();
  }
}
