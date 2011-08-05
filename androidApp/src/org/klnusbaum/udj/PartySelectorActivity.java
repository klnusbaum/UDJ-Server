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
public class PartySelectorActivity extends Activity{

  private AccountManager am;
  private Account account;
  private static final int ACCOUNT_REQUEST = 0;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    setContentView(R.layout.party_selector);
    am = AccountManager.get(this);
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
        break;
      }
    }
    //TODO Throw exception if no user is found.
  }

  public void preformLogin(View view){

  }
}

