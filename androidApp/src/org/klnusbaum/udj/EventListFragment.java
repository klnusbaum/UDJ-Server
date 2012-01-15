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
import android.app.AlertDialog;

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
import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.network.EventCommService.EventJoinError;


public class EventListFragment extends ListFragment implements 
  LoaderManager.LoaderCallbacks<EventsLoader.EventsLoaderResult>,
  LocationListener
{
  private static final String TAG = "EventListFragment";
  private static final String PROG_DIALOG_TAG = "prog_dialog";
  private static final String EVENT_JOIN_FAIL_TAG = "prog_dialog";
  private static final String LOCATION_EXTRA = "location";
  private static final String EVENT_SEARCH_QUERY = 
    "org.klnusbaum.udj.EventSearchQuery";
  private static final String EVENT_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.EventSearchType";
  private static final String LOCATION_STATE_EXTRA = 
    "org.klnusbaum.udj.LastKnownLocation";
  private static final String LAST_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.LastSearchType";
  private static final int ACCOUNT_CREATION = 0;

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
  private AccountManager am;

  private BroadcastReceiver eventJoinedReceiver = new BroadcastReceiver(){
    public void onReceive(Context context, Intent intent){
      Log.d(TAG, "Recieved event broadcats");
      dismissProgress();
      getActivity().unregisterReceiver(eventJoinedReceiver);
      AccountManager am = AccountManager.get(context);
      if(intent.getAction().equals(Constants.JOINED_EVENT_ACTION)){
        Intent eventActivityIntent = new Intent(context, EventActivity.class);
        startActivity(eventActivityIntent); 
      }
      else if(intent.getAction().equals(Constants.EVENT_JOIN_FAILED_ACTION)){
        displayEventJoinFail();
      }
    }
  };

  public void onActivityCreated(Bundle icicle){
    super.onActivityCreated(icicle);
    am = AccountManager.get(getActivity());
    Account[] udjAccounts = am.getAccountsByType(Constants.ACCOUNT_TYPE);
    Log.d(TAG, "Accounts length was " + udjAccounts.length);
    if(udjAccounts.length < 1){
      Intent getAccountIntent = new Intent(getActivity(), AuthActivity.class);
      startActivityForResult(getAccountIntent, ACCOUNT_CREATION);
      return;
    }
    else if(udjAccounts.length == 1){
      account=udjAccounts[0];
    }
    else{
      account=udjAccounts[0];
      //TODO implement if there are more than 1 account
    }
    if(icicle != null){
      if(icicle.containsKey(LOCATION_STATE_EXTRA)){
        lastKnown = (Location)icicle.getParcelable(LOCATION_STATE_EXTRA);
      }
      if(icicle.containsKey(LAST_SEARCH_TYPE_EXTRA)){
        restoreLastSearch(icicle);
      }
    }
    setEmptyText(getActivity().getString(R.string.no_event_items));
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
  }

  public void onActivityResult(
    int requestCode, int resultCode, Intent data)
  {
    switch(requestCode){
    case ACCOUNT_CREATION:
      if(resultCode == Activity.RESULT_OK){
        account = (Account)data.getParcelableExtra(Constants.ACCOUNT_EXTRA);
      }
      else{
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
      }
      break;
    }
  }

  public void onResume(){
    super.onResume();
    if(account != null){
      if(isShowingProgress()){
        EventJoinError joinError = EventJoinError.valueOf(
          am.getUserData(account, Constants.EVENT_JOIN_ERROR));
        if(joinError != EventJoinError.NO_ERROR && isShowingProgress()){
          dismissProgress();
          displayEventJoinFail();
          //TODO inform user joining failed.
        }
        else{
          registerEventListener();
        }
      }
      int inEvent = Integer.valueOf(
        am.getUserData(account, Constants.IN_EVENT_DATA));
      if(inEvent == Constants.IN_EVENT_FLAG){
        long eventId = Long.valueOf(
          am.getUserData(account, Constants.LAST_EVENT_ID_DATA));
        Intent startEventActivity = 
          new Intent(getActivity(), EventActivity.class);
        startActivity(startEventActivity);
        return;
      }

      if(eventAdapter == null || eventAdapter.getCount() ==0){
        refreshEventList();
      }
      
    }
  }

  private boolean isShowingProgress(){
    return 
      getActivity().getSupportFragmentManager().findFragmentByTag(
        PROG_DIALOG_TAG)
      != 
      null;
  }

  public void onPause(){
    super.onPause();
    try{
      getActivity().unregisterReceiver(eventJoinedReceiver);
    }
    catch(IllegalArgumentException e){

    }
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

  public void setEventSearch(EventSearch newSearch){
    lastSearch = newSearch;
    refreshEventList();
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

  @Override
  public void onListItemClick(ListView l, View v, int position, long id){
    showProgress();
    Intent joinEventIntent = new Intent(
      Intent.ACTION_INSERT, 
      Constants.EVENT_URI, 
      getActivity(), 
      EventCommService.class);
    Event toJoin = (Event)eventAdapter.getItem(position);
    joinEventIntent.putExtra(
      Constants.EVENT_ID_EXTRA, 
      toJoin.getEventId());
    joinEventIntent.putExtra(
      Constants.EVENT_NAME_EXTRA, 
      toJoin.getName());
    joinEventIntent.putExtra(
      Constants.EVENT_HOSTNAME_EXTRA, 
      toJoin.getHostName());
    joinEventIntent.putExtra(
      Constants.EVENT_HOST_ID_EXTRA, 
      toJoin.getHostId());
    joinEventIntent.putExtra(
      Constants.EVENT_LAT_EXTRA,
      toJoin.getLatitude());
    joinEventIntent.putExtra(
      Constants.EVENT_LONG_EXTRA, 
      toJoin.getLongitude());
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
      setEmptyText(getString(R.string.events_load_error));
      break;
    case NO_CONNECTION:
      setEmptyText(getString(R.string.no_network_connection));
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
    registerEventListener();
    ProgressFragment progFragment = new ProgressFragment();
    progFragment.show(
      getActivity().getSupportFragmentManager(), PROG_DIALOG_TAG);
  }

  private void registerEventListener(){
    getActivity().registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.JOINED_EVENT_ACTION));
    getActivity().registerReceiver(
      eventJoinedReceiver, 
      new IntentFilter(Constants.EVENT_JOIN_FAILED_ACTION));
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

  private void displayEventJoinFail(){
    DialogFragment newFrag = new EventJoinFailDialog(account);
    newFrag.show(
      getActivity().getSupportFragmentManager(), EVENT_JOIN_FAIL_TAG);
  }

  public static class EventJoinFailDialog extends DialogFragment{
    private Account account;

    public EventJoinFailDialog(Account account){
      super();
      this.account = account;
    }

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
      AccountManager am = AccountManager.get(getActivity());
      EventJoinError joinError = EventJoinError.valueOf(
        am.getUserData(account, Constants.EVENT_JOIN_ERROR));
      String message; 
      switch(joinError){
      case SERVER_ERROR:
        message = getString(R.string.server_join_fail_message); 
        break;
      case AUTHENTICATION_ERROR:
        message = getString(R.string.auth_join_fail_message); 
        break;
      case EVENT_OVER_ERROR:
        message = getString(R.string.event_over_join_fail_message); 
        break;
      case NO_NETWORK_ERROR:
        message = getString(R.string.no_network_join_fail_message); 
        break;
      default:
        message = getString(R.string.unknown_error_message);
      }
      return new AlertDialog.Builder(getActivity())
        .setTitle(R.string.event_join_fail_title)
        .setMessage(message)
        .setPositiveButton(
          android.R.string.ok,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              dismiss();
            }
          })
        .create();
    }
  }
} 
