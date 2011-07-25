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

import android.app.ListActivity;
import android.widget.SimpleCursorAdapter;
import android.os.Bundle;
import android.database.Cursor;

/**
 * An Activity which displays the party's current
 * available libary.
 */
public class LibraryActivity extends ListActivity{
  
  /** Adapter used to help display the contents of the library. */
  SimpleCursorAdapter libraryAdapter;
  
  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    Cursor libraryCursor = managedQuery(
      UDJPartyProvider.LIBRARY_URI, null, null, null, null); 
    libraryAdapter = new SimpleCursorAdapter(
      this,
      R.layout.library_list_item,
      libraryCursor,
      new String[] {UDJPartyProvider.SONG_COLUMN, UDJPartyProvider.ARTIST_COLUMN},
      new int[] {R.id.librarySongName, R.id.libraryArtistName}
    );
    setListAdapter(libraryAdapter);
  /*  ListView lv = getListView();
    lv.setTextFilterEnabled(true);
   	registerForContextMenu(lv); */
  }
}
