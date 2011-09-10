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
public class SyncAdapter extends AbstractThreadedSyncAdapter{
  private final Context context;
  private GregorianCalendar playlistLastUpdate;
  private GregorianCalendar partiesLastUpdate;

  private AccountManager am;

  public static final String PLAYLIST_SYNC_EXTRA = "playlist_sync";
  public static final String LIBRARY_SEARCH_QUERY_EXTRA = "search_query";

  /*private static final String[] playlistProjection = new String[]{
    UDJPartyProvider.PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SERVER_PLAYLIST_ID_COLUMN, 
    UDJPartyProvider.SYNC_STATE_COLUMN};*/
  private static final String playlistWhereClause = 
    UDJPartyProvider.SYNC_STATE_COLUMN + "=?";

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
    final boolean syncPlaylist = extras.getBoolean(PLAYLIST_SYNC_EXTRA, false);
    final long partyId = 
      extras.getLong(Party.PARTY_ID_EXTRA, Party.INVALID_PARTY_ID);
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

      //Sync playlist if requested
      if(syncPlaylist){


        //Get a list of all the playlist entries we want the server
        // to update
        List<PlaylistEntry> addedEntries = getChangePlaylistEntries(
            provider, UDJPartyProvider.NEEDS_INSERT_MARK);
        List<PlaylistEntry> votedUpEntries = getChangePlaylistEntries(
            provider, UDJPartyProvider.NEEDS_UP_VOTE);
        List<PlaylistEntry> votedDownEntries = getChangePlaylistEntries(
            provider, UDJPartyProvider.NEEDS_DOWN_VOTE);
 
        //Tell the server to do the update via REST
        //A retrieve it's response.
        List<PlaylistEntry> updatedPlaylistEntries =
          ServerConnection.getPlaylistUpdate(
            partyId, 
            addedEntries, 
            votedUpEntries, 
            votedDownEntries,
            playlistLastUpdate);
        Log.i("TAG", "Number of pe's " + updatedPlaylistEntries.size());
  
        //Process the REST response from the server.
        RESTProcessor.processPlaylistEntries(
          updatedPlaylistEntries, context);
  
        playlistLastUpdate = (GregorianCalendar)GregorianCalendar.getInstance();
      }

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
      am.invalidateAuthToken(
        context.getString(R.string.account_type), authtoken);
      syncResult.stats.numAuthExceptions++;
    }
    catch(final ParseException e){
      syncResult.stats.numParseExceptions++;
    }
    catch(final JSONException e){
      Log.e("TAG", "JSON EXception!!!!");
      Log.e("TAG", e.getMessage());
      syncResult.stats.numParseExceptions++;
    }
    catch(final RemoteException e){
      syncResult.stats.numParseExceptions++;
    }
    catch(final OperationApplicationException e){
      syncResult.stats.numParseExceptions++;
    }
  }

  private List<PlaylistEntry> 
    getChangePlaylistEntries(ContentProviderClient provider, String whereArg)
    throws RemoteException
  {

    Cursor needsUpdating = provider.query(
      UDJPartyProvider.PLAYLIST_URI,
      null,
      playlistWhereClause,
      new String[] {whereArg},
      null
    );
    List<PlaylistEntry> toReturn = 
      new ArrayList<PlaylistEntry>(needsUpdating.getCount());
   /* ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();*/
    while(needsUpdating.moveToNext()){
      //TODO actually impelement this correctly.
      toReturn.add(PlaylistEntry.valueOf(needsUpdating));
/*    batchOps.add(getChangeToUpdatingOperation(c.getInt(0), c.getString(2)));
      if(batchOps.size() == 50){
        provider.applyBatch(batchOps); 
        batchOps.clear();
      }*/
    } 
    //provider.applyBatch(batchOps); 
    needsUpdating.close();
    return toReturn;
  }

/*  private static ContentProviderOperation getChangeToUpdatingOperation(
    int plid, String currentSyncState)
  {
    ContentProviderOperation.Builder builder = 
      ContentProviderOperation.newUpdateQuery(UDJPartyProvider.PLAYLIST_URI);
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
  }*/
}
