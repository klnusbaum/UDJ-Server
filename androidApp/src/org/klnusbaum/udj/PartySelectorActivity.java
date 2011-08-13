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

import android.app.Activity;
import android.os.Bundle;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.Intent;
import android.view.View;

import org.klnusbaum.udj.auth.AuthActivity;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PartySelectorActivity extends Activity
  implements 
  LoaderManager.LoaderCallbacks<List<ArrayList> >,
  AccountManagerCallback<Bundle>
{

  private AccountManager am;
  private Account account;
  private String password;
  private static final int ACCOUNT_REQUEST = 0;
  private static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
  private static final String PASSWORD_EXTRA = "org.klnusbaum.udj.password";


  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    setContentView(R.layout.party_selector);
    am = AccountManager.get(this);
    account = savedInstanceState.getParcelable(ACCOUNT_EXTRA);
    if(account == null){
      getAccount()
    }
    password = savedInstanceState.getString(PASSWORD_EXTRA);
  }

  private void getAccount(){
    Account[] accs = am.getAccountsByType(getString(R.string.account_type));
    if(accs.length < 1){
      Intent getNewAccountIntent = new Intent(this, AuthActivity.class);
      getNewAccountIntent.putExtra(AuthActivity.AUTHTOKEN_TYPE_EXTRA, getString(R.string.authtoken_type));
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
  protected void onActivityResult(int requestCode, int resultCode, Intent data){
    switch(resultCode){
      case ACCOUNT_REQUEST: onAddAccountResult(resultCode, data); break;
    }
  }

  private void onAddAccountResult(int resultCode, Intent data){
    if(resultCode == Activity.RESULT_CANCELED){
      setResult(Activity.RESULT_CANCELED);
      finish();
    }
    Account[] udjAccounts = am.getAccountsByType(getString(R.string.account_type));
    String username = data.getStringExtra(AuthActivity.USERNAME_EXTRA);
    boolean foundAddedUser;
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

  protected void onSaveInstanceState(Bundle outState){
    outState.put(ACCOUNT_EXTRA, account);
    outState.put(PASSWORD_EXTRA, account);
  }

  protected void onResume(){
    if(password ==null){
      getPassword();
    }
  }

  private void getPassword(){
    //TODO throw error if account is some how not set yet.
    am.getAuthToken(
      account, 
      getString(R.string.authtoken_type), 
      null, this, this, null);
  }

  @Override
  public void run(AccountManagerFuture result){
    Bundle bundle;
    try{
      bundle = result.getResult();
      Intent intent = (Intent)bundle.get(AccountManager.KEY_INTENT);
      if(intent != null){
        startActivity(intent);
      }
      else{
        password = bundle.getString(AccountManager.KEY_AUTHTOKEN);
      }
    }
    catch(OperationCancledException e){
      e.printStackTrace();
    }
    catch(AuthenticatorException e){
      e.printStackTrace();
    }
    catch(IOException e){
      e.printStackTrace();
    }
  }
  

  public Loader<Cursor> onCreateLoader(int id, Bundle args){

  }

  public void onLoadFinished(Loader<Cursor> loader, Cursor data){

  }

  public void onLoaderReset(Loader<Cursor> loader){

  }

  public static class PartiesLoader extends AsyncTaskLoader<List<Party> >{
    
    public List<Party> loadInBackground(){
      ServerConnection serverConn = 
    }

  }

}

