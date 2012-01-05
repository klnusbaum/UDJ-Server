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
import android.content.BroadcastReceiver;
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
import android.content.IntentFilter;
import android.util.Log;
import android.widget.Toast;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.DialogFragment;
import android.support.v4.app.ListFragment;
import android.support.v4.content.Loader;
import android.support.v4.app.LoaderManager;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;

import org.apache.http.auth.AuthenticationException;

import org.json.JSONException;
import org.json.JSONObject;

import org.klnusbaum.udj.network.EventCommService;
import org.klnusbaum.udj.containers.Event;


public class EventListFragment extends ListFragment implements 
  LoaderManager.LoaderCallbacks<EventsLoader.EventsLoaderResult>,
  LocationListener
{
  private static final String TAG = "EventListFragment";
  private static final String PROG_DIALOG_TAG = "prog_dialog";
  private static final String LOCATION_EXTRA = "location";
  private static final String EVENT_SEARCH_QUERY = 
    "org.klnusbaum.udj.EventSearchQuery";
  private static final String EVENT_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.EventSearchType";
  private static final String LOCATION_STATE_EXTRA = 
    "org.klnusbaum.udj.LastKnownLocation";
  private static final String LAST_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.LastSearchType";

  private interface EventSearch{
    public abstract Bundle getLoaderArgs();
    public abstract int getSearchType();
  }

  public static class LocationEventSearch implements EventSearch{
    Location givenLocation;
    public static final int SEARCH_TYPE = 0; 

    public LocationEventSearch(Location givenLocation){
      this.givenLocation = givenLocation;
    }

    public void setLocation(Location newLocation){
      givenLocation = newLocation; 
    }

    public Bundle getLoaderArgs(){
      Bundle loaderArgs = new Bundle(); 
      loaderArgs.putInt(EVENT_SEARCH_TYPE_EXTRA, SEARCH_TYPE);
      loaderArgs.putParcelable(LOCATION_EXTRA, givenLocation);
      return loaderArgs;
    }
    
    public int getSearchType(){
      return SEARCH_TYPE; 
    }
  }

  public static class NameEventSearch implements EventSearch{
    String query;
    private static final int SEARCH_TYPE = 1; 
    public NameEventSearch(String query){
      this.query = query;
    }

    public Bundle getLoaderArgs(){
      Bundle loaderArgs = new Bundle();
      loaderArgs.putInt(EVENT_SEARCH_TYPE_EXTRA, SEARCH_TYPE);
      loaderArgs.putString(EVENT_SEARCH_QUERY, query);
      return loaderArgs;
    }

    public int getSearchType(){
      return SEARCH_TYPE;
    }

    public String getQuery(){
      return query; 
    }
  }


  private EventListAdapter eventAdapter;
  private LocationManager lm;
  private Location lastKnown = null;
  private Account account = null;
  private EventSearch lastSearch = null;

  private BroadcastReceiver eventJoinedReceiver = new BroadcastReceiver(){
    public void onReceive(Context context, Intent intent){
      Log.d(TAG, "Recieved event broadcats");
      dismissProgress();
      getActivity().unregisterReceiver(eventJoinedReceiver);
      if(intent.getAction().equals(Constants.JOINED_EVENT_ACTION)){
        Intent eventActivityIntent = new Intent(context, EventActivity.class);
        eventActivityIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
        startActivity(eventActivityIntent); 
      }
      else if(intent.getAction().equals(Constants.EVENT_JOIN_FAILED_ACTION)){
        //TODO inform user of event joining failure
      }
    }
  };

  public void onActivityCreate(Bundle icicle){
    super.onCreate(icicle);
    //TODO we shouldn't just assume the arguements are there...
    //that said it always should be.
    if(icicle != null){
      if(icicle.containsKey(LOCATION_STATE_EXTRA)){
        lastKnown = (Location)icicle.getParcelable(LOCATION_STATE_EXTRA);
      }
      if(icicle.containsKey(LAST_SEARCH_TYPE_EXTRA)){
        restoreLastSearch(icicle);
      }
    }
    setEmptyText(getActivity().getString(R.string.no_party_items));
    eventAdapter = new EventListAdapter(getActivity());
    setListAdapter(eventAdapter);
    setListShown(false);
  }

  public void onStart(){
    super.onStart();
    lm = (LocationManager)getActivity().getSystemService(
      Context.LOCATION_SERVICE);
    List<String> providers = lm.getProviders(false);
    if(providers.contains(LocationManager.GPS_PROVIDER)){
      lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,0, 50, this);
      if(lastKnown == null){
        lastKnown = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
      }
    }
    if(providers.contains(LocationManager.NETWORK_PROVIDER)){
      lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,0, 50, this);
      if(lastKnown == null){
        lastKnown = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
      }
    }
    if(lastSearch == null){
      lastSearch = new LocationEventSearch(lastKnown);
    }
    refreshEventList();
  }

  public void setEventSearch(EventSearch newSearch){
    lastSearch = newSearch;
    refreshEventList();
  }

  public void onStop(){
    super.onStop();
    lm.removeUpdates(this); 
  }

  public void onSaveInstanceState(Bundle outState){
    super.onSaveInstanceState(outState);
    outState.putParcelable(LOCATION_STATE_EXTRA, lastKnown);
    outState.putInt(EVENT_SEARCH_TYPE_EXTRA, lastSearch.getSearchType());
    if(lastSearch.getSearchType() == NameEventSearch.SEARCH_TYPE){
      outState.putString(
        EVENT_SEARCH_QUERY, ((NameEventSearch)lastSearch).getQuery());
    }
  }

  private void restoreLastSearch(Bundle icicle){
    int searchType = icicle.getInt(LAST_SEARCH_TYPE_EXTRA, -1);
    switch(searchType){
    case LocationEventSearch.SEARCH_TYPE:
      lastSearch = new LocationEventSearch(lastKnown);
      break;
    case NameEventSearch.SEARCH_TYPE:
      lastSearch = new NameEventSearch(
        icicle.getString(EVENT_SEARCH_QUERY));
      break;
    } 
  }

  public void onLocationChanged(Location location){
    lastKnown = location;
    if(lastSearch.getSearchType() == LocationEventSearch.SEARCH_TYPE){
      ((LocationEventSearch)lastSearch).setLocation(lastKnown);
    }
  }

  public void onProviderDisabled(String provider){}
  public void onProviderEnabled(String provider){}
  public void onStatusChanged(String provider, int status, Bundle extras){}

  public void refreshEventList(){
    getLoaderManager().restartLoader(0, lastSearch.getLoaderArgs(), this);
  }

  public void setAccount(Account account){
    this.account = account;
    if(isAdded()){
      refreshEventList();
    }
  }
  
  @Override
  public void onListItemClick(ListView l, View v, int position, long id){
    showProgress();
    Intent joinEventIntent = new Intent(
      Intent.ACTION_INSERT, 
      Constants.EVENT_URI, 
      getActivity(), 
      EventCommService.class);
    joinEventIntent.putExtra(
      Constants.EVENT_ID_EXTRA, 
      eventAdapter.getItemId(position));
    joinEventIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
    getActivity().startService(joinEventIntent);
  }

  public Loader<EventsLoader.EventsLoaderResult> onCreateLoader(
    int id, Bundle args)
  {
    int eventSearchType = args.getInt(EVENT_SEARCH_TYPE_EXTRA, 
      -1);
    if(eventSearchType == LocationEventSearch.SEARCH_TYPE){
      return new EventsLoader(
        getActivity(), 
        account,
        (Location)args.getParcelable(LOCATION_EXTRA));
    }
    else if(eventSearchType == NameEventSearch.SEARCH_TYPE){
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
    case NO_ACCOUNT:
      setEmptyText(getString(R.string.no_account_error));
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
    getActivity().registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.JOINED_EVENT_ACTION));
    getActivity().registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.EVENT_JOIN_FAILED_ACTION));
    ProgressFragment progFragment = new ProgressFragment();
    progFragment.show(
      getActivity().getSupportFragmentManager(), PROG_DIALOG_TAG);
  }

  private void dismissProgress(){
    ProgressFragment pd = (ProgressFragment)getActivity().getSupportFragmentManager().findFragmentByTag(PROG_DIALOG_TAG);
    pd.dismiss();
  }

  private class ProgressFragment extends DialogFragment{
    public Dialog onCreateDialog(Bundle icicle){
      final ProgressDialog dialog = new ProgressDialog(getActivity());
      dialog.setMessage(getActivity().getString(R.string.joining_event));
      dialog.setIndeterminate(true);
      dialog.setCancelable(true);
      dialog.setOnCancelListener(new DialogInterface.OnCancelListener(){
        public void onCancel(DialogInterface dialog){
          getActivity().unregisterReceiver(eventJoinedReceiver);
        }
      });
      return dialog;
    }
  }
} 
