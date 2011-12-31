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
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;

import android.app.Activity;
import android.os.Bundle;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.Intent;
import android.content.Context;
import android.view.View;
import android.app.SearchManager;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.actionbar.ActionBarActivity;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class EventSelectorActivity extends ActionBarActivity{

  private static final int ACCOUNT_CREATION = 0;
  private Account account;
  private AccountManager am;
  private EventListFragment list;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    am = AccountManager.get(this);
    Account[] udjAccounts = am.getAccountsByType(Constants.ACCOUNT_TYPE);
    if(udjAccounts.length < 1){
      //TODO implement if there aren't any account
      Intent getAccountIntent = new Intent(this, AuthActivity.class);
      startActivityForResult(getAccountIntent, ACCOUNT_CREATION);
    }
    else if(udjAccounts.length == 1){
      account=udjAccounts[0];
      showEventUI();
    }
    else{
      account=udjAccounts[0];
      showEventUI();
      //TODO implement if there are more than 1 account
    }
  }

  private void showEventUI(){
    if(Long.valueOf(am.getUserData(account, Constants.EVENT_ID_DATA)) !=
      Constants.NO_EVENT_ID)
    {
      Intent eventActivityIntent = new Intent(this, EventActivity.class);
      eventActivityIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
      startActivity(eventActivityIntent); 
    }
    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      list = new EventListFragment();
      Bundle listArgs = new Bundle();
      listArgs.putParcelable(Constants.ACCOUNT_EXTRA, account);
      list.setArguments(listArgs);
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  protected void onActivityResult(
    int requestCode, int resultCode, Intent data)
  {
    if(resultCode == Activity.RESULT_OK){
      account = (Account)data.getParcelableExtra(Constants.ACCOUNT_EXTRA);
      showEventUI();
    }
    else{
      setResult(Activity.RESULT_CANCELED);
      finish();
    }
  }

  protected void onNewIntent(Intent intent){
    if(Intent.ACTION_SEARCH.equals(intent.getAction())){
      list.searchByName(intent.getStringExtra(SearchManager.QUERY));
    }
    else{
      super.onNewIntent(intent);
    }
  }
}
