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
import android.accounts.AuthenticatorException;;

import java.util.GregorianCalendar;
import java.util.List;
import java.io.IOException;
import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.R;


/**
 * Adapter used to sync up with the UDJ server.
 */
public class SyncAdapter extends AbstractThreadedSyncAdapter{
  private final Context context;
  private GregorianCalendar lastUpdated;
  private AccountManager am;

  public static final String LIBRARY_SYNC_EXTRA = "library_sync";

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
    am = AccountManager.get(context);
  }

  @Override
  public void onPerformSync(Account account, Bundle extras, String authority,
    ContentProviderClient provider, SyncResult syncResult)
  {
    boolean synclibrary = extras.getBoolean(LIBRARY_SYNC_EXTRA, false);
    String authtoken = null;
    try{
      authtoken = am.blockingGetAuthToken(
        account, context.getString(R.string.authtoken_type), true);
      if(synclibrary){
        List<LibraryEntry> updatedLibEntries = 
          ServerConnection.getLibraryUpdate(account, authtoken, lastUpdated);
        RESTProcessor.processLibraryEntries(updatedLibEntries);
      }
      List<PlaylistEntry> changedPlaylistEntries = 
        getAndMarkPlaylistEntriesToUpdate(provider);
      List<PlaylistEntry> updatedPlaylistEntries =
        ServerConnection.getPlaylistUpdate(
          account, authtoken, changedPlaylistEntries, lastUpdated);
      RESTProcessor.processPlaylistEntries(newPlaylistEntries);
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
    /*catch(final AuthenticationException e){
      am.invalidateAuthToken(
        context.getString(R.string.account_type), authtoken);
      syncResult.stats.numAuthExceptions++;
    }*/
    catch(final ParseException e){
       syncResult.stats.numParseExceptions++;
    }
  }

  private List<PlaylistEntries> 
    getAndMarkPlaylistEntriesToUpdate(ContentProviderClient provider)
  {
    static final String[] projection = 
      new String[] {PLAYLIST_ID_COLUMN, PLAYLIST_LIBRARY_ID_COLUMN, 
        SYNC_STATE_COLUMN}
    static final String whereClause = 
      UDJPartyProvider.SYNC_STATE_COLUMN + "=? OR " + 
      UDJPartyProvider.SYNC_STATE_COLUMN + "=? OR " + 
      UDJPartyProvider.SYNC_STATE_COLUMN + "=?";
    static final String[] whereArgs = new String[]
      {NEEDS_UP_VOTE, NEEDS_DOWN_VOTE, NEEDS_INSERT_MARK};

    Cursor needsUpdating = provider.query(
      UDJPartyProvider.PLAYLIST_URI,
      projection,
      whereClause,
      whereArgs,
      null
    );
    List<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>(c.getCount());
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    while(c.moveToNext()){
      toReturn.add(new PlaylistEntry(c));
      batchOps.add(getChangeToUpdatingOperation(c.getInt(0), c.getString(2)));
      if(batchOps.size() == 50){
        provider.applyBatch(batchOps); 
        batchOps.clear();
      }
    } 
    provider.applyBatch(batchOps); 
    c.close();
    return toReturn;
  }

  private static ContentProviderOperation getChangeToUpdatingOperation(
    int plid, String currentSyncState)
  {
    ContentProviderClient.Builder builder = 
      ContentProviderClient.newUpdateQuery(UDJPartyProvider.PLAYLIST_URI);
    builder = builder.withSelection(
      UDJPartyProvider.PLAYLIST_ID_COLUMN + "=?", 
      new String(plid));
    if(currentSyncState.equals(UDJPartyProvider.NEEDS_INSERT_MARK)){
      builder = builder.withValue(
        UDJPartyProvider.SYNC_STATE_COLUMN, 
        UDJPartyProvider.INSERTING_MARK);
    }
    else{
      builder = builder.withValue(
        UDJPartyProvider.SYNC_STATE_COLUMN, 
        UDJPartyProvider.UPDATEING_MARK);
    }
    return builder.build();
  }
}
