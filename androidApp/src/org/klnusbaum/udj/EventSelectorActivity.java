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

import android.os.AsyncTask;
import android.content.ContentResolver;
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
import android.widget.Toast;
import android.app.ProgressDialog;
import android.net.Uri;
import android.app.SearchManager;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.Event;
import org.klnusbaum.udj.containers.VoteRequests;
import org.klnusbaum.udj.actionbar.ActionBarActivity;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class EventSelectorActivity extends ActionBarActivity{

  private static final int SELECTING_PARTY_DIALOG = 0;
  private static final String EVENT_SEARCH_QUERY = 
    "org.klnusbaum.udj.EventSearchQuery";
  private static final String EVENT_SEARCH_TYPE_EXTRA = 
    "org.klnusbaum.udj.EventSearchType";
  private static final int EVENT_LOCATION_SERACH = 0; 
  private static final int EVENT_NAME_SEARCH = 1; 
  private static final String LOCATION_EXTRA = "location";
  private static final int ACCOUNT_CREATION = 0;
  private static final String LOCATION_STATE_EXTRA = 
    "org.klnusbaum.udj.LastKnownLocation";
  private Account account;
  /** Keep track of the progress dialog so we can dismiss it */
  private ProgressDialog mProgressDialog = null;
  private EventLoginTask loginTask;
  private EventListFragment list = null;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      list = new EventListFragment();
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  protected void onActivityResult(
    int requestCode, int resultCode, Intent data)
  {
    if(resultCode == Activity.RESULT_OK){
      account = (Account)data.getParcelableExtra(Constants.ACCOUNT_EXTRA);
    }
    else{
      setResult(Activity.RESULT_CANCELED);
      finish();
    }
  }
  public void onEventJoinResponse(final long eventId){
    loginTask = null;
    hideProgress();
    if(eventId > 0){
      Intent viewEventIntent = new Intent(getApplicationContext(),
        EventActivity.class);
      viewEventIntent.putExtra(Constants.EVENT_ID_EXTRA, eventId);
      viewEventIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
      startActivity(viewEventIntent);
    }
    else{
      Toast toast = Toast.makeText(getApplicationContext(), "Login failed",  
        Toast.LENGTH_LONG);
      toast.show();
    }
  }

  public void onEventJoinCancel(){
    loginTask = null;
    hideProgress();
  }

  private void showProgress(){
      showDialog(0);
  }

  private void hideProgress(){
    if(mProgressDialog != null){
      mProgressDialog.dismiss();
      mProgressDialog = null;
    }
  }

  /*
   * {@inheritDoc}
   */
  @Override
  protected Dialog onCreateDialog(int id) {
    final ProgressDialog dialog = new ProgressDialog(this);
    dialog.setMessage(getText(R.string.joining_event));
    dialog.setIndeterminate(true);
    dialog.setCancelable(true);
    dialog.setOnCancelListener(new DialogInterface.OnCancelListener() {
      public void onCancel(DialogInterface dialog) {
        Log.i("Event Selection", "user cancelling authentication");
        if(loginTask != null) {
          loginTask.cancel(true);
         }
       }
    });
    // We save off the progress dialog in a field so that we can dismiss
    // it later. We can't just call dismissDialog(0) because the system
    // can lose track of our dialog if there's an orientation change.
    mProgressDialog = dialog;
    return dialog;
  }

  public class EventLoginTask extends AsyncTask<Long, Void, Long>{
    private static final String EVENT_LOGIN_TAG = "EventLoginTask";
   
    private AccountManager am; 
    private Account account; 
    private ContentResolver cr;
    public EventLoginTask(
      AccountManager am, Account account, ContentResolver cr)
    {
      super();
      this.am = am;
      this.account = account; 
      this.cr = cr;
    }
  
    protected Long doInBackground(Long... params){
      try{
        String authToken = 
          am.blockingGetAuthToken(account, "", true);  
        long userId = Long.valueOf(
          am.getUserData(account, Constants.USER_ID_DATA));
        if(ServerConnection.joinEvent(params[0], userId, authToken)){
          UDJEventProvider.eventCleanup(cr);          
          HashMap<Long,Long> previousRequests = ServerConnection.getAddRequests(
            userId, params[0], authToken);
          UDJEventProvider.setPreviousAddRequests(cr, previousRequests);
          VoteRequests previousVotes = 
            ServerConnection.getVoteRequests(userId, params[0], authToken);
          UDJEventProvider.setPreviousVoteRequests(cr, previousVotes);
          return params[0]; 
        }
      }
      catch(IOException e){
        Log.e(EVENT_LOGIN_TAG, "IO exception when logging in" + e.getMessage());
        //TODO notify the user
      }
      catch(AuthenticatorException e){
        Log.e(EVENT_LOGIN_TAG, 
          "Authentiator exception when logging in" + e.getMessage());
        //TODO notify the user
      }
      catch(OperationCanceledException e){
        Log.e(EVENT_LOGIN_TAG, 
          "Op cancled exception when logging in" + e.getMessage());
        //TODO notify user
      }
      catch(JSONException e){
        Log.e(EVENT_LOGIN_TAG, 
          "JSON exception when logging in" + e.getMessage());
        //TODO notify user
      }
      catch(AuthenticationException e){
        Log.e(EVENT_LOGIN_TAG, 
          "Authentication exception when logging in" + e.getMessage());
        //TODO notify user
      }
      return new Long(-1);
    }
  
    protected void onPostExecute(final Long eventId){
      onEventJoinResponse(eventId);
    }
 
    protected void onCancelled(){
      onEventJoinCancel();
    }
  }

  @Override
  protected void onNewIntent(Intent intent){
    if(Intent.ACTION_SEARCH.equals(intent.getAction())){
      list.searchByName(intent.getStringExtra(SearchManager.QUERY));
    }
    else{
      super.onNewIntent(intent);
    }
  }


  public class EventListFragment extends ListFragment implements 
    LoaderManager.LoaderCallbacks<EventsLoader.EventsLoaderResult>,
    LocationListener
  {

    public void searchByName(String query){
      Bundle loaderArgs = new Bundle();
      loaderArgs.putInt(EVENT_SEARCH_TYPE_EXTRA, EVENT_NAME_SEARCH);
      loaderArgs.putString(EVENT_SEARCH_QUERY, query);
      getLoaderManager().restartLoader(0, loaderArgs, this);
    }

    private EventListAdapter eventAdapter;
    private LocationManager lm;
    Location lastKnown;

    public void onActivityCreated(Bundle icicle){
      super.onActivityCreated(icicle);
      if(icicle != null && icicle.containsKey(LOCATION_STATE_EXTRA)){
        lastKnown = (Location)icicle.getParcelable(LOCATION_STATE_EXTRA);
      }
      else{
        lastKnown = null;
      }
      loginTask = null;
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
        Intent getAccountIntent = 
          new Intent(getActivity(), AuthActivity.class);
        getActivity().startActivityForResult(
          getAccountIntent, ACCOUNT_CREATION);
      }
      else if(udjAccounts.length == 1){
        account=udjAccounts[0];
      }
      else{
        account=udjAccounts[0];
        //TODO implement if there are more than 1 account
      }
      lm = (LocationManager)getSystemService(
        Context.LOCATION_SERVICE);
      lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,0, 50, this);
      lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,0, 50, this);
    }

    public void onResume(){
      super.onResume();
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

    public void onProviderDisabled(String provider){

    }

    public void onProviderEnabled(String provider){

    }

    public void onStatusChanged(String provider, int status, Bundle extras){

    }
    
    @Override
    public void onListItemClick(ListView l, View v, int position, long id){
      Long[] eventId = new Long[]{eventAdapter.getItemId(position)};
      loginTask = (EventLoginTask)new EventLoginTask(
        AccountManager.get(getActivity()), 
        account, 
        getContentResolver());
      loginTask.execute(eventId); 
      showProgress();
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
  } 
}

