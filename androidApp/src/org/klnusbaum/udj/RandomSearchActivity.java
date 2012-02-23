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
import android.app.SearchManager;

/**
 * An Activity which displays the results of a library search.
 */
public class RandomSearchActivity extends EventEndedListenerActivity{

  private static final String TAG = "RandomActivty";
  private RandomSearchFragment searchFrag;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      searchFrag = new RandomSearchFragment();
      fm.beginTransaction().add(android.R.id.content, searchFrag).commit();
    }
  }
}
