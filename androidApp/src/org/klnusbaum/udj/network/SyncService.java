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
package org.klnusbaum.udj.sync;


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
import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.UDJPartyProvider;
import org.klnusbaum.udj.R;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class SyncService extends IntentService{
  private GregorianCalendar playlistLastUpdate;
  private GregorianCalendar partiesLastUpdate;

  private AccountManager am;

  public static final String ACCOUNT_EXTRA = "account";

  /*private static final String[] playlistProjection = new String[]{
    UDJPartyProvider.PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SYNC_STATE_COLUMN};*/
  private static final String playlistWhereClause = 
    UDJPartyProvider.SYNC_STATE_COLUMN + "=?";

  @Override
  public onCreate(){
    super.onCreate();
    am = AccountManager.get(this);
  }

  @Override
  public void onHandleIntent(Intent intent){
    final Account account = (Account)intent.getParcelableExtra(ACCOUNT_EXTRA);
    final boolean syncPlaylist = 
      intent.getBooleanExtra(PLAYLIST_SYNC_EXTRA, false);
    final long partyId = 
      intent.getLongExtra(Party.PARTY_ID_EXTRA, Party.INVALID_PARTY_ID);
    String authtoken = null;
    try{
      if(partyId == Party.INVALID_PARTY_ID){
        throw new OperationApplicationException("Not given a valid party id");
      }
      //Get Authtoken
      authtoken = am.blockingGetAuthToken(
        account, context.getString(R.string.authtoken_type), true);
      if(authtoken == null){
        //TODO throw exeception if authtoken is null
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

}
