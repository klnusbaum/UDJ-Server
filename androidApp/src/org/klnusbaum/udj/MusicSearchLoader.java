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
import org.klnusbaum.udj.exceptions.EventOverException;

public class MusicSearchLoader 
  extends AsyncTaskLoader<MusicSearchLoader.MusicSearchResult>
{
 
  public enum MusicSearchError{
    NO_ERROR, 
    EVENT_ENDED_ERROR,
    NO_SEARCH_ERROR,
    SERVER_ERROR,
    AUTHENTICATION_ERROR};
  private static final String TAG = "MusicSearchLoader";

  public static class MusicSearchResult{
    private List<LibraryEntry> res;
    private MusicSearchError error;
  
    public MusicSearchResult(List<LibraryEntry> res){
      this.res = res;
      this.error = MusicSearchError.NO_ERROR;
    }

    public MusicSearchResult(List<LibraryEntry> res, MusicSearchError error){
      this.res = res;
      this.error = error;
    }

    public List<LibraryEntry> getResults(){
      return res;
    }

    public MusicSearchError getError(){
      return error;
    }
  }


  private String query;
  private Account account;

  public MusicSearchLoader(
    Context context, String query, Account account)
  {
    super(context);
    this.query = query;
    this.account = account;
  }

  public MusicSearchResult loadInBackground(){
    return doSearch(true);
  }

  private MusicSearchResult doSearch(boolean attemptReauth){
    if(query != null){
      AccountManager am = AccountManager.get(getContext());
      String authToken = "";
      try{
        authToken = am.blockingGetAuthToken(account, "", true);
      }
      catch(IOException e){
        //TODO this might actually be an auth error
        return new MusicSearchResult(null, 
          MusicSearchError.AUTHENTICATION_ERROR);
      }
      catch(AuthenticatorException e){
        return new MusicSearchResult(null, 
          MusicSearchError.AUTHENTICATION_ERROR);
      }
      catch(OperationCanceledException e){
        return new MusicSearchResult(null, 
          MusicSearchError.AUTHENTICATION_ERROR);
      }

      try{
        long eventId = 
          Long.valueOf(am.getUserData(account, Constants.LAST_EVENT_ID_DATA));
        List<LibraryEntry> list = 
          ServerConnection.availableMusicQuery(query, eventId, authToken);
        return new MusicSearchResult(list);
      }
      catch(JSONException e){
        return new MusicSearchResult(null, 
          MusicSearchError.SERVER_ERROR);
      }
      catch(ParseException e){
        return new MusicSearchResult(null, 
          MusicSearchError.SERVER_ERROR);
      }
      catch(IOException e){
        return new MusicSearchResult(null, 
          MusicSearchError.SERVER_ERROR);
      }
      catch(AuthenticationException e){
        if(attemptReauth){
          Log.d(TAG, "soft auth failure");
          am.invalidateAuthToken(Constants.ACCOUNT_TYPE, authToken);
          return doSearch(false);
        }
        else{
          Log.d(TAG, "hard auth failure");
          return new MusicSearchResult(null, 
            MusicSearchError.AUTHENTICATION_ERROR);
        }
      }
      catch(EventOverException e){
        return new MusicSearchResult(null, MusicSearchError.EVENT_ENDED_ERROR);
      }
    }
    return new MusicSearchResult(null, MusicSearchError.NO_SEARCH_ERROR);
  }

  @Override
  protected void onStartLoading(){
    forceLoad();
  }
}
