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

import java.util.List;

import org.klnusbaum.udj.PullToRefresh.RefreshableListFragment;
import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.containers.Event;
import org.klnusbaum.udj.network.EventCommService;
import org.klnusbaum.udj.network.EventCommService.EventJoinError;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.support.v4.app.DialogFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.Loader;
import android.util.Log;
import android.view.View;
import android.widget.ListView;

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


public class EventListFragment extends RefreshableListFragment implements 
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
  private static final int ACCOUNT_CREATION_REQUEST_CODE = 0;
  private static final int GET_PASSWORD_REQUEST_CODE = 1;

  private interface EventSearch{
    public abstract Bundle getLoaderArgs();
    public abstract int getSearchType();
  }

	@Override
	protected void doRefreshWork() {
		refreshList();
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
        handleEventJoinFail();
      }
    }
  };

  public void onCreate(Bundle icicle){
    super.onCreate(icicle);
    setHasOptionsMenu(true);
  }

  public void onActivityCreated(Bundle icicle){
    super.onActivityCreated(icicle);
    am = AccountManager.get(getActivity());
    Account[] udjAccounts = am.getAccountsByType(Constants.ACCOUNT_TYPE);
    Log.d(TAG, "Accounts length was " + udjAccounts.length);
    if(udjAccounts.length < 1){
      Intent getAccountIntent = new Intent(getActivity(), AuthActivity.class);
      startActivityForResult(getAccountIntent, ACCOUNT_CREATION_REQUEST_CODE);
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
    case ACCOUNT_CREATION_REQUEST_CODE:
      if(resultCode == Activity.RESULT_OK){
        account = (Account)data.getParcelableExtra(Constants.ACCOUNT_EXTRA);
      }
      else{
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
      }
      break;
    case GET_PASSWORD_REQUEST_CODE: 
      Log.d(TAG, "Got Password request back");
      if(resultCode == Activity.RESULT_OK){
        Log.d(TAG, "request code was ok");
        String eventPassword = data.getStringExtra(Constants.EVENT_PASSWORD_EXTRA);
        Event toJoin = Event.unbundle(data.getBundleExtra(Constants.EVENT_EXTRA));
        joinEvent(toJoin, eventPassword);
      }
      break;
    }
  }

  public void onResume(){
    super.onResume();
    if(account != null){
      int eventState = Utils.getEventState(getActivity(), account);
      Log.d(TAG, "Checking Event State");
      if(eventState == Constants.JOINING_EVENT){
        Log.d(TAG, "Is joining");
        Log.d(TAG, "Reregistering event listener");
        registerEventListener();
      }
      else if(eventState == Constants.EVENT_JOIN_FAILED){
        Log.d(TAG, "Event Joined Failed");
        dismissProgress();
        handleEventJoinFail();
        //TODO inform user joining failed.
      }
      else if(eventState == Constants.IN_EVENT){
        Log.d(TAG, "Already signed into event. Checking Progress visibility");
        if(isShowingProgress()){
          Log.d(TAG, "Determined progress is indeed showing");
          dismissProgress();
        }
        long eventId = Long.valueOf(
          am.getUserData(account, Constants.LAST_EVENT_ID_DATA));
        Intent startEventActivity = 
          new Intent(getActivity(), EventActivity.class);
        startActivity(startEventActivity);
        return;
      }
      else if(eventAdapter == null || eventAdapter.getCount() ==0){
        refreshList();
      }
    }
  }

  public void onPause(){
    super.onPause();
    if(account != null){
      int eventState = Utils.getEventState(getActivity(), account);
      if(eventState == Constants.JOINING_EVENT){
        getActivity().unregisterReceiver(eventJoinedReceiver);
      }
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
    refreshList();
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

  @Override
  public void onListItemClick(ListView l, View v, int position, long id){
    Event toJoin = (Event)eventAdapter.getItem(position);
    if(toJoin.getHasPassword()){
      getPasswordForEvent(toJoin);
    }
    else{
      joinEvent(toJoin);
    }
  }

  public void getPasswordForEvent(Event toJoin){
    Bundle eventBundle = toJoin.bundleUp();
    Intent getPasswordIntent = new Intent(getActivity(), EventPasswordActivity.class);
    getPasswordIntent.putExtra(Constants.EVENT_EXTRA, eventBundle);
    startActivityForResult(getPasswordIntent, GET_PASSWORD_REQUEST_CODE);
  }

  public void joinEvent(Event toJoin){
    joinEvent(toJoin, "");
  }

  public void joinEvent(Event toJoin, String password){
    Log.d(TAG, "Joining Event");
    am.setUserData(
      account,
      Constants.EVENT_STATE_DATA,
      String.valueOf(Constants.JOINING_EVENT));
    showProgress();
    Intent joinEventIntent = new Intent(
      Intent.ACTION_INSERT,
      Constants.EVENT_URI,
      getActivity(),
      EventCommService.class);
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
    joinEventIntent.putExtra(Constants.EVENT_PASSWORD_EXTRA, password);
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
    refreshDone();
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
    setListAdapter(null);
  }

  public void refreshList(){
    getLoaderManager().restartLoader(0, lastSearch.getLoaderArgs(), this);
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
    Log.d(TAG, "Listener registered");
  }

  private boolean isShowingProgress(){
    ProgressFragment pd =
      (ProgressFragment)getActivity().getSupportFragmentManager().findFragmentByTag(PROG_DIALOG_TAG);
    return pd != null && pd.getDialog().isShowing();
  }

  private void dismissProgress(){
    ProgressFragment pd = (ProgressFragment)getActivity().getSupportFragmentManager().findFragmentByTag(PROG_DIALOG_TAG);
    pd.dismiss();
  }

  public static class ProgressFragment extends DialogFragment{

    public Dialog onCreateDialog(Bundle icicle){
      final ProgressDialog dialog = new ProgressDialog(getActivity());
      dialog.setMessage(getActivity().getString(R.string.joining_event));
      dialog.setIndeterminate(true);
      return dialog;
    }
  }

  private void handleEventJoinFail(){
    DialogFragment newFrag = new EventJoinFailDialog();
    AccountManager am = AccountManager.get(getActivity());
    EventJoinError joinError = EventJoinError.valueOf(
      am.getUserData(account, Constants.EVENT_JOIN_ERROR));
    Bundle args = new Bundle();
    args.putInt(Constants.EVENT_JOIN_ERROR_EXTRA, joinError.ordinal());
    newFrag.setArguments(args);
    newFrag.show(
      getActivity().getSupportFragmentManager(), EVENT_JOIN_FAIL_TAG);
  }

  public static class EventJoinFailDialog extends DialogFragment{

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
      Bundle args = getArguments();
      EventJoinError joinError = 
        EventJoinError.values()[args.getInt(Constants.EVENT_JOIN_ERROR_EXTRA)];
      AlertDialog.Builder builder = new AlertDialog.Builder(getActivity())
        .setTitle(R.string.event_join_fail_title);
      String message; 
      switch(joinError){
      case SERVER_ERROR:
        message = getString(R.string.server_join_fail_message); 
        break;
      case AUTHENTICATION_ERROR:
        message = getString(R.string.auth_join_fail_message); 
        break;
      case EVENT_OVER_ERROR:
        ((EventSelectorActivity)getActivity()).refreshList();
        message = getString(R.string.event_over_join_fail_message); 
        break;
      case NO_NETWORK_ERROR:
        message = getString(R.string.no_network_join_fail_message); 
        break;
      default:
        message = getString(R.string.unknown_error_message);
      }
      return builder
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
