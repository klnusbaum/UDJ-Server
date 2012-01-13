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
import android.view.Window;
import android.app.SearchManager;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MenuInflater;
import android.os.Build;


/**
 * Class used for displaying the contents of the Playlist.
 */
public class EventSelectorActivity extends FragmentActivity{

  private Account account;
  private AccountManager am;
  private EventListFragment list;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    if(Build.VERSION.SDK_INT < Build.VERSION_CODES.HONEYCOMB){ 
      requestWindowFeature(Window.FEATURE_NO_TITLE);
    }

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      list = new EventListFragment();
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  protected void onNewIntent(Intent intent){
    if(Intent.ACTION_SEARCH.equals(intent.getAction())){
      list.setEventSearch(new EventListFragment.NameEventSearch(
        intent.getStringExtra(SearchManager.QUERY)));
    }
    else{
      super.onNewIntent(intent);
    }
  }

  public boolean onCreateOptionsMenu(Menu menu){
    MenuInflater inflater = getMenuInflater();
    inflater.inflate(R.menu.event_list, menu);
    return true;
  }

  public boolean onOptionsItemSelected(MenuItem item){
    switch (item.getItemId()) {
    case R.id.menu_refresh:
      list.refreshEventList();
      /*getActionBarHelper().setRefreshActionItemState(true);
      getWindow().getDecorView().postDelayed(
        new Runnable() {
          @Override
          public void run() {
            getActionBarHelper().setRefreshActionItemState(false);
          }
       }, 1000);*/
       break;
     case R.id.menu_search:
       startSearch(null, false, null, false);
       break;
    }
    return super.onOptionsItemSelected(item);
  }

}
