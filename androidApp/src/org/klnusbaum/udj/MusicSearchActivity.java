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

import android.os.Bundle;
import android.content.Intent;
import android.content.Context;
import android.util.Log;
import android.accounts.Account;
import android.app.SearchManager;

import org.klnusbaum.udj.Constants;

/**
 * An Activity which displays the results of a library search.
 */
public class MusicSearchActivity extends EventEndedListenerActivity{

  private static final String TAG = "MusicActivity";
  private String searchQuery;
  private MusicSearchFragment searchFrag;
  
  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    searchQuery = getIntent().getStringExtra(SearchManager.QUERY);

    //TODO before calling fragment, to get ID and give that to it.
    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      Bundle queryArgs = new Bundle();
      queryArgs.putString(MusicSearchFragment.SEARCH_QUERY_EXTRA, searchQuery);
      searchFrag = new MusicSearchFragment();
      searchFrag.setArguments(queryArgs);
      fm.beginTransaction().add(android.R.id.content, searchFrag).commit();
    }
  }

  protected void onNewIntent(Intent intent){
    Log.d(TAG, "In on new intent");
    if(Intent.ACTION_SEARCH.equals(intent.getAction())){
      searchQuery = intent.getStringExtra(SearchManager.QUERY);
      getIntent().putExtra(SearchManager.QUERY, searchQuery);
      searchFrag.setSearchQuery(searchQuery);
    }
  }
}
