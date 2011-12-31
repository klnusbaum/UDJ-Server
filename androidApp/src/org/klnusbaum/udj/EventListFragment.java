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

import android.os.Bundle;
import android.app.Activity;
import android.content.ContentResolver;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.location.LocationManager;
import android.location.Location;
import android.location.LocationListener;
import android.content.DialogInterface;
import android.app.ProgressDialog;
import android.app.Dialog;
import android.widget.ListView;
import android.content.Context;
import android.view.View;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import android.support.v4.app.LoaderManager;
import android.support.v4.content.Loader;
import android.support.v4.app.ListFragment;

import java.io.IOException;
import java.util.HashMap;

import org.apache.http.auth.AuthenticationException;

import org.json.JSONException;
import org.json.JSONObject;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.Event;


public class EventListFragment extends ListFragment implements 
  LoaderManager.LoaderCallbacks<EventsLoader.EventsLoaderResult>,
  LocationListener
{
  private static final int EVENT_LOCATION_SERACH = 0; 
  private static final int EVENT_NAME_SEARCH = 1; 
  private static final String LOCATION_EXTRA = "location";
  private static final String EVENT_SEARCH_QUERY = 
    "org.klnusbaum.udj.EventSearchQuery";
  private static final String EVENT_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.EventSearchType";
  private static final String LOCATION_STATE_EXTRA = 
    "org.klnusbaum.udj.LastKnownLocation";

  private EventListAdapter eventAdapter;
  private LocationManager lm;
  private Location lastKnown;
  private Account account;

  private BroadcastReceiver eventJoinedReceiver = new BroadcastReceiver(){
    public void onReceive(Context context, Intent intent){
      dismissProgress();
      unregisterEventReceivers();
      if(intent.getAction().equals(Constants.JOINED_EVENT_ACTION)){
        Intent eventActivityIntent(context, EventActivity.class);
        eventActivityIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
        startActivity(eventActivityIntent); 
      }
    }
  }

      

  public void onCreate(Bundle icicle){
    super.onCreate(icicle);
    //TODO we shouldn't just assume the arguements are there...
    //that said it always should be.
    account = (Account)getArguments().getParcelable(Constants.ACCOUNT_EXTRA);
    if(icicle != null && icicle.containsKey(LOCATION_STATE_EXTRA)){
      lastKnown = (Location)icicle.getParcelable(LOCATION_STATE_EXTRA);
    }
    else{
      lastKnown = null;
    }
    setEmptyText(getActivity().getString(R.string.no_party_items));
    eventAdapter = new EventListAdapter(getActivity());
    setListAdapter(eventAdapter);
    setListShown(false);
  }

  public void onResume(){
    super.onResume();
    lm = (LocationManager)getSystemService(
      Context.LOCATION_SERVICE);
    lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,0, 50, this);
    lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,0, 50, this);
    if(lastKnown == null){
      lastKnown = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
    }
    if(lastKnown == null){
      lastKnown = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
    }
    Bundle loaderArgs = new Bundle(); 
    loaderArgs.putInt(EVENT_SEARCH_TYPE_EXTRA, EVENT_LOCATION_SERACH);
    loaderArgs.putParcelable(LOCATION_EXTRA, lastKnown);
    getLoaderManager().initLoader(0, loaderArgs, this);
  }

  public void onPause(){
    super.onPause();
    lm.removeUpdates(this); 
  }

  public void onSaveInstanceState(Bundle outState){
    super.onSaveInstanceState(outState);
    outState.putParcelable(LOCATION_STATE_EXTRA, lastKnown);
  }

  public void onLocationChanged(Location location){
    lastKnown = location;
  }

  public void onProviderDisabled(String provider){}
  public void onProviderEnabled(String provider){}
  public void onStatusChanged(String provider, int status, Bundle extras){}
  
  @Override
  public void onListItemClick(ListView l, View v, int position, long id){
    Long[] eventId = new Long[]{eventAdapter.getItemId(position)};
    showProgress();
    Intent joinEventIntent = new Intent(
      Intent.ACTION_INSERT, null, getActivity(), EventCommService.class);
    joinEventIntent.putExtra(Constants.EVENT_ID_EXTRA, eventId);
    startService(joinEventIntent);
  }

  public void searchByName(String query){
    Bundle loaderArgs = new Bundle();
    loaderArgs.putInt(EVENT_SEARCH_TYPE_EXTRA, EVENT_NAME_SEARCH);
    loaderArgs.putString(EVENT_SEARCH_QUERY, query);
    getLoaderManager().restartLoader(0, loaderArgs, this);
  }

  public Loader<EventsLoader.EventsLoaderResult> onCreateLoader(
    int id, Bundle args)
  {
    int eventSearchType = args.getInt(EVENT_SEARCH_TYPE_EXTRA, 
      -1);
    if(eventSearchType == EVENT_LOCATION_SERACH){
      return new EventsLoader(
        getActivity(), 
        account,
        (Location)args.getParcelable(LOCATION_EXTRA));
    }
    else if(eventSearchType == EVENT_NAME_SEARCH){
      return new EventsLoader(
        getActivity(), 
        account,
        args.getString(EVENT_SEARCH_QUERY));
    }
    else{
      return null;
    }
  }

  public void onLoadFinished(Loader<EventsLoader.EventsLoaderResult> loader, 
    EventsLoader.EventsLoaderResult data)
  {
    switch(data.getError()){
    case NO_ERROR:
      eventAdapter = 
        new EventListAdapter(getActivity(), data.getEvents(), null);
      setListAdapter(eventAdapter);
      break;
    case NO_LOCATION:
      setEmptyText(getString(R.string.no_location_error));
      break;
    case SERVER_ERROR:
      setEmptyText(getString(R.string.party_load_error));
      break;
    }

    if(isResumed()){
      setListShown(true);
    }
    else if(isVisible()){
      setListShownNoAnimation(true);
    }
  }

  public void onLoaderReset(Loader<EventsLoader.EventsLoaderResult> loader){
    eventAdapter = new EventListAdapter(getActivity());
  }

  private void showProgress(){
    registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.JOINED_EVENT_ACTION));
    registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.JOINED_EVENT_ACTION));
    ProgressFragment progFragment = new ProgressFragment();
    progFragment.show(getSupportFragmentManager(), PROG_DIALOG_TAG);
  }

  private void dismissProgres(){
    ProgressFragment pd = (ProgressFragment)getSupportFragmentManager().
      findFragmentByTag(PROG_DIALOG_TAG);
    pd.dismiss();
  }

  private void unregisterEventReceivers(){
    unregisterReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.JOINED_EVENT_ACTION));
    unregisterReceiver(
      eventJoinFailedReceiver, 
      new IntentFilter(Constants.EVENT_JOIN_FAILED_ACTION));
  }


  private static class ProgressFragment extends DialogFragment{
    public Dialog onCreateDialog(Bundle icicle){
      final ProgressDialog dialog = new ProgressDialog(getActivity());
      dialog.setMessage(getString(R.string.joining_event));
      dialog.setIndeterminate(true);
      dialog.setCancelable(true);
      dialog.setOnCancelListener(new DialogInterface.OnCancelListener(){
        public void onCancel(DialogInterface dialog){
          ((EventListFragment)getActivity()).removeEventListener();
        }
      }
      return dialog;
    }
  }
} 
