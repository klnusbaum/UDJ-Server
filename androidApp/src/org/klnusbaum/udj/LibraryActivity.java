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
import android.content.ContentValues;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.ImageButton;
import android.content.Context;
import android.view.LayoutInflater;
import android.widget.CursorAdapter;
import android.util.Log;

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

  private class LibraryAdapter extends CursorAdapter{

    public LibraryAdapter(Context context, Cursor c){
      super(context, c);
    }

    @Override
    public void bindView(View view, Context context, Cursor cursor){
      int libraryId = cursor.getInt(cursor.getColumnIndex(UDJPartyProvider.LIBRARY_ID_COLUMN));
      
      TextView songName =
        (TextView)view.findViewById(R.id.librarySongName);

      TextView artistName =
        (TextView)view.findViewById(R.id.libraryArtistName);
      
      ImageButton addSong = 
        (ImageButton)view.findViewById(R.id.lib_add_button);
      addSong.setTag(String.valueOf(libraryId));
      addSong.setOnClickListener(new View.OnClickListener(){
        public void onClick(View v){
          addSongClick(v);
        }
      });
    }
  
    @Override
    public View newView(Context context, Cursor cursor, ViewGroup parent){
      LayoutInflater inflater = (LayoutInflater)context.getSystemService(
        Context.LAYOUT_INFLATER_SERVICE);
      View itemView = inflater.inflate(R.layout.library_list_item, null);
      return itemView;
    }

    private void addSongClick(View view){
      String libId = view.getTag().toString(); 
      ContentValues values = new ContentValues();
      values.put(UDJPartyProvider.LIBRARY_ID_COLUMN,Integer.valueOf(libId) );
      getContentResolver().insert(
        UDJPartyProvider.PLAYLIST_URI,
        values);
    }

  }  
}
