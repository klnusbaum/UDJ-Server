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

import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.ListFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.Loader;
import android.support.v4.content.AsyncTaskLoader;

import android.app.Activity;
import android.os.Bundle;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.Intent;
import android.content.Context;
import android.view.View;
import android.accounts.OperationCanceledException;
import android.accounts.AuthenticatorException;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.widget.ListView;
import android.util.Log;
import android.content.DialogInterface;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.app.Dialog;
import android.location.LocationManager;
import android.location.Location;
import android.location.LocationListener;


import java.io.IOException;
import java.util.List;
import java.util.ArrayList;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.Event;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class EventSelectorActivity extends FragmentActivity{

  private static final int SELECTING_PARTY_DIALOG = 0;
  private static final String ACCOUNT_EXTRA = "account";
  private static final String LOCATION_EXTRA = "location";

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      EventListFragment list = new EventListFragment();
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  public class EventListFragment extends ListFragment implements 
    LoaderManager.LoaderCallbacks<List<Event> >,
    LocationListener
  {
    private EventListAdapter eventAdapter;
    private String authToken;
    private Account account;
    private LocationManager lm;

    public void onActivityCreated(Bundle savedInstanceState){
      super.onActivityCreated(savedInstanceState);
      account = null;
      setEmptyText(getActivity().getString(R.string.no_party_items));
      eventAdapter = new EventListAdapter(getActivity());
      setListAdapter(eventAdapter);
      setListShown(false);
      Account[] udjAccounts = 
        AccountManager.get(getActivity()).getAccountsByType(
          Constants.ACCOUNT_TYPE);
      if(udjAccounts.length < 1){
        //TODO implement if there aren't any account
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
        return;
      }
      else if(udjAccounts.length == 1){
        account=udjAccounts[0];
      }
      else{
        account=udjAccounts[0];
        //TODO implement if there are more than 1 account
      }
    }

    public void onResume(){
      super.onResume();
      lm = (LocationManager)getSystemService(
        Context.LOCATION_SERVICE);
      lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,0, 50, this);
      //lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,0, 50, this);

      Location lastKnown = 
        lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
      Bundle loaderArgs = new Bundle(); 
      loaderArgs.putParcelable(ACCOUNT_EXTRA, account);
      loaderArgs.putParcelable(LOCATION_EXTRA, lastKnown);
      getLoaderManager().initLoader(0, loaderArgs, this);
    }

    public void onPause(){
      super.onPause();
      lm.removeUpdates(this); 
    }

    public void onLocationChanged(Location location){
      Bundle loaderArgs = new Bundle(); 
      loaderArgs.putParcelable(ACCOUNT_EXTRA, account);
      loaderArgs.putParcelable(LOCATION_EXTRA, location);
      getLoaderManager().restartLoader(0, loaderArgs, this);
    }

    public void onProviderDisabled(String provider){

    }

    public void onProviderEnabled(String provider){

    }

    public void onStatusChanged(String provider, int status, Bundle extras){

    }

    
    @Override
    public void onListItemClick(ListView l, View v, int position, long id){
      /*selectPartyThread = ServerConnection.loginToParty(
        partyAdpater.getPartyId(position), 
        selectionHandler, 
        getActivity());
      getActivity().showDialog(SELECTING_PARTY_DIALOG);*/
    }

    public Loader<List<Event> > onCreateLoader(int id, Bundle args){
      return new EventsLoader(
        getActivity(), 
        (Account)args.getParcelable(ACCOUNT_EXTRA),
        (Location)args.getParcelable(LOCATION_EXTRA));
    }
  
    public void onLoadFinished(Loader<List<Event> > loader, List<Event> data){
      if(data == null){
        setEmptyText(getString(R.string.party_load_error));
      }
      else{
        for(Event e: data){
          eventAdapter.add(e);
        }
      }

      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }
  
    public void onLoaderReset(Loader<List<Event> > loader){
      eventAdapter.clear();
    }
  } 

  public static class EventsLoader extends AsyncTaskLoader<List<Event> >{
     
    Context context;
    Account account;
    Location location;
    List<Event> events;

    public EventsLoader(Context context, Account account, Location location){
      super(context);
      this.context = context;
      this.account = account;
      this.location = location;
      events = null;
    }
    
    @Override
    protected void onStartLoading(){
      if(takeContentChanged() || events==null){
        forceLoad();
      }
    }
 
    public List<Event> loadInBackground(){
      try{
        AccountManager am = AccountManager.get(context);
        String authToken = am.blockingGetAuthToken(account, "", true); 
          return ServerConnection.getNearbyEvents(location, authToken);
      }
      catch(JSONException e){
        //TODO notify the user
      }
      catch(IOException e){
        //TODO notify the user
      }
      catch(AuthenticatorException e){
        //TODO notify the user
      }
      catch(AuthenticationException e){
        //TODO notify the user
      }
      catch(OperationCanceledException e){
        //TODO notify user
      }
      return null;
    }

  }

  /*
  @Override
  protected Dialog onCreateDialog(int id){
    switch(id){
    case SELECTING_PARTY_DIALOG:
      final ProgressDialog progDialog = new ProgressDialog(this);
      progDialog.setMessage(getText(R.string.logging_into_party));
      progDialog.setIndeterminate(true);
      progDialog.setCancelable(true);
      progDialog.setOnCancelListener(new DialogInterface.OnCancelListener(){
        public void onCancel(DialogInterface dialog){
          if(selectPartyThread != null){
            selectPartyThread.interrupt();
          }
        }
      });
      return progDialog;
    default:
      return null;
    }
  }
  
  public void onPartySelection(boolean success, long partyId){
    dismissDialog(SELECTING_PARTY_DIALOG);
    removeDialog(SELECTING_PARTY_DIALOG);
    if(!success){
      //TODO Handle bad login
      return;
    }
    final Intent partyIntent = new Intent(this, PartyActivity.class);
    partyIntent.putExtra(
      Party.PARTY_ID_EXTRA, 
      partyId);
    partyIntent.putExtra(
      PartyActivity.ACCOUNT_EXTRA,
      account);
    startActivity(partyIntent);
  }*/
}

