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

import java.util.GregorianCalendar;

import org.klnusbaum.udj.network.ServerConnection;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class SyncAdapter extends AbstractThreadedSyncAdapter{
  private final Context context;
  private GregorianCalendar lastUpdated;
  private AccountManager am;

  /**
   * Constructs a SyncAdapter.
   *
   * @param context The context from with the sync adapter is being
   * created.
   * @param autoInitialize Whether or not to automatically initialize.
   */
  public SyncAdapter(Context context, boolean autoInitialize){
    super(context, autoInitialize);
    this.context=context;
    am = AccountManager(context);
  }

  @Override
  public void onPerformSync(Account account, Bundle extras, String authority,
    ContentProviderClient provider, SyncResult syncResult)
  {
    boolean synclibrary = extras.getBoolean(LIBRARY_SYNC_EXTRA, false);
    String authtoken = null;
    try{
      authotoken = am.blockingGetAuthToken(account, context.getString(R.string.authtoken_type), true);
      if(synclibrary){
        List<LibraryEntry> updatedLibEntries = 
          ServerConnection.syncLibrary(acount, authtoken, lastUpdated);
        RESTProcessor.processNewLibEntries(updatedLibEntries);
      }
      List<PlaylistEntry> newPlaylistEntries =
        ServerConnection.syncPlaylist(account, authtoken, lastUpdated);
      RESTProcessor.processNewPlaylistEntries(newPlaylistEntries);
      lastUpdated = (GregorianCalendar)GregorianCalendar.getInstance();
    } 
    catch(final AuthenticatorException e){
      syncResult.stats.numParseExceptions++;
    } 
    catch(final OperationCanceledException e){

    }
    catch(final IOException e){
      syncResult.stats.numIoExceptions++;
    }
    catch(final AuthenticationException e){
      mAccountManager.invalidateAuthToken(Constants.ACCOUNT_TYPE, authtoken);
      syncResult.stats.numAuthExceptions++;
    }
    catch(final ParseException e){
       syncResult.stats.numParseExceptions++;
    }
  }
}
