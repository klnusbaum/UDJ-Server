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
import android.accounts.AccountManagerCallback;
import android.accounts.AccountManagerFuture;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.util.Log;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.Party;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PartySelectorActivity extends FragmentActivity{




  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      ParyListFragment list = new ParyListFragment();
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }


  }

  public static class ParyListFragment extends ListFragment
  implements 
    LoaderManager.LoaderCallbacks<List<Party> >,
    AccountManagerCallback<Bundle>
  {
    private AccountManager am;
    private Account account;
    private String password;
    private static final int ACCOUNT_REQUEST = 0;
    private static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
    private static final String PASSWORD_EXTRA = "org.klnusbaum.udj.password";
    private static final int PARTIES_LOADER = 0;
    private ArrayAdapter<Party> partyAdpater;

    public void onActivityCreated(Bundle savedInstanceState){
      super.onActivityCreated(savedInstanceState);
      setEmptyText(getActivity().getString(R.string.no_party_items));
      partyAdpater = new ArrayAdapter<Party>(
        getActivity(), R.layout.party_item, R.id.item);
      setListAdapter(partyAdpater);
      setListShown(false);
      am = AccountManager.get(getActivity());
      account = null;
      password = null;
      if(savedInstanceState != null){
        account = savedInstanceState.getParcelable(ACCOUNT_EXTRA);
        password = savedInstanceState.getString(PASSWORD_EXTRA);
      }
      if(account == null){
        getAccount();
      }
    }

    private void getAccount(){
      Account[] accs = am.getAccountsByType(getString(R.string.account_type));
      if(accs.length < 1){
        Intent getNewAccountIntent = 
          new Intent(getActivity(), AuthActivity.class);
        getNewAccountIntent.putExtra(
          AuthActivity.AUTHTOKEN_TYPE_EXTRA, 
          getString(R.string.authtoken_type));
        startActivityForResult(getNewAccountIntent, ACCOUNT_REQUEST);
      }
      else if(accs.length >1){
        //TODO select form a list of accounts
      }
      else{
        account = accs[0];
        getPassword();
        //TODO make sure password isn't null
      }
    }
  
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data){
      switch(requestCode){
        case ACCOUNT_REQUEST: onAddAccountResult(resultCode, data); break;
      }
    }
  
    private void onAddAccountResult(int resultCode, Intent data){
      if(resultCode == Activity.RESULT_CANCELED){
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
      }
      Account[] udjAccounts = 
        am.getAccountsByType(getString(R.string.account_type));
      String username = data.getStringExtra(AccountManager.KEY_ACCOUNT_NAME);
      boolean foundAddedUser = false;
      for(Account acc: udjAccounts){
        if(acc.name.equals(username)){
          foundAddedUser = true;
          account = acc;
          getPassword();
          break;
        }
      }
      //TODO Throw exception if no user is found.
    }
  
    @Override
    public void onSaveInstanceState(Bundle outState){
      super.onSaveInstanceState(outState);
      outState.putParcelable(ACCOUNT_EXTRA, account);
      outState.putString(PASSWORD_EXTRA, password);
    }
  
    @Override
    public void onResume(){
      super.onResume();
      getPassword();
    }
  
    private void getPassword(){
      //TODO throw error if account is some how not set yet.
      if(account != null && password == null){
        am.getAuthToken(
          account, 
          getString(R.string.authtoken_type), 
          null, getActivity(), this, null);
      }
    }

    @Override
    public void run(AccountManagerFuture<Bundle> result){
      Bundle bundle;
      try{
        bundle = result.getResult();
        Intent intent = (Intent)bundle.get(AccountManager.KEY_INTENT);
        if(intent != null){
          startActivity(intent);
        }
        else{
          password = bundle.getString(AccountManager.KEY_AUTHTOKEN);
          final Bundle loaderArgs = new Bundle();
          loaderArgs.putParcelable(PartiesLoader.ACCOUNT_EXTRA, account);
          loaderArgs.putString(PartiesLoader.AUTHTOKEN_EXTRA, password);
          //getActivity().runOnUiThread(new Runnable(){
            //public void run(){
          getLoaderManager().restartLoader(PARTIES_LOADER, loaderArgs, ParyListFragment.this);
            //}
          //});
        }
      }
      catch(OperationCanceledException e){
        e.printStackTrace();
      }
      catch(AuthenticatorException e){
        e.printStackTrace();
      }
      catch(IOException e){
        e.printStackTrace();
      }
    }
    
    @Override
    public void onListItemClick(ListView l, View v, int position, long id){
      Party partyClicked = (Party)getListView().getItemAtPosition(position);
      Intent partyIntent = new Intent(getActivity(), PartyActivity.class);
      partyIntent.putExtra(
        Party.PARTY_ID_EXTRA, partyClicked.getPartyId());
      startActivity(partyIntent);
    }
  
    public Loader<List<Party> > onCreateLoader(int id, Bundle args){
      switch(id){
  
      case PARTIES_LOADER:
        //TODO enforce that the account and autoken aren't null;
        Account argAccount = args.getParcelable(PartiesLoader.ACCOUNT_EXTRA);
        String argAuthToken = args.getString(PartiesLoader.AUTHTOKEN_EXTRA);
        return new PartiesLoader(getActivity(), argAccount, argAuthToken);
      }
      return null;
    }
  
    public void onLoadFinished(Loader<List<Party> > loader, List<Party> data){
      for(Party p: data){
        partyAdpater.add(p);
      }
      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }
  
    public void onLoaderReset(Loader<List<Party> > loader){
      Log.i("TAG", "IN RESTART!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
      partyAdpater.clear();
    }
  } 

  public static class PartiesLoader extends AsyncTaskLoader<List<Party> >{
     
    public static final String ACCOUNT_EXTRA = "account";
    public static final String AUTHTOKEN_EXTRA = "auth_token";
    Account account;
    String authtoken;
    Context context;
 
    public PartiesLoader(Context context, Account account, String authtoken){
      super(context);
      this.account = account;
      this.authtoken = authtoken;
    }
    
    public List<Party> loadInBackground(){
      try{
        Log.i("TAG", "loading in background");
        return ServerConnection.getNearbyParties(account, authtoken);
      }
      catch(JSONException e){
        //TODO notify the user
      }
      catch(IOException e){
        //TODO notify the user
      }
      catch(AuthenticationException e){
        //TODO notify the user
      }
      return null;
    }

  }

}

