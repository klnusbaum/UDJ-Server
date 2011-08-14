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
import android.support.v4.content.CursorLoader;
import android.support.v4.content.Loader;
import android.support.v4.widget.CursorAdapter;

import android.os.Bundle;
import android.database.Cursor;
import android.content.ContentValues;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.ImageButton;
import android.content.Context;
import android.view.LayoutInflater;
import android.util.Log;

/**
 * An Activity which displays the party's current
 * available libary.
 */
public class LibraryActivity extends FragmentActivity{
  
  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    if(savedInstanceState != null){
      partyId = savedInstanceState.getLong(PartyActivity.PARTY_ID_EXTRA);
    }
    else{
      partyId = getIntent().getLongExtra(PartyActivity.PARTY_ID_EXTRA, Party.INVALID_PARTY_ID);
      if(partyId == Party.INVALID_PARTY_ID){
        setResult(Activity.RESULT_CANCELED);
        finish();
      }
    }

    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      Bundle partyBundle = new Bundle();
      partyBundle.putLong(PartyActivity.PARTY_ID_EXTRA, partyId);
      LibraryFragment list = new LibraryFragment();
      list.setArguments(partyBundle);
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  public static class LibraryFragment extends ListFragment
    implements LoaderManager.LoaderCallbacks<Cursor>
  {
    /** Adapter used to help display the contents of the library. */
    LibraryAdapter libraryAdapter;
    
    private long partyId;
    
    @Override
    public void onActivityCreated(Bundle savedInstanceState){
      super.onActivityCreated(savedInstanceState);

      setEmptyText(getActivity().getString(R.string.no_library_songs));
      //setHasOptionsMenu(true);

      //TODO throw some kind of error if the party id is null. Although it never should be.
      Bundle args = getArguements();
      if(args.containsKey(PartyActivity.PARTY_ID_EXTRA)){
        partyId = args.getLong(PartyActivity.PARTY_ID_EXTRA);
      }
      else{
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
      }

      libraryAdapter = new LibraryAdapter(getActivity(), null);
      setListAdapter(libraryAdapter);
      setListShown(false);
      getLoaderManager().initLoader(0,null, this);
    }

    public Loader<Cursor> onCreateLoader(int id, Bundle args){
      return new CursorLoader(
        getActivity(), 
        UDJPartyProvider.LIBRARY_URI, 
        null,
        "partyId=?",
        new String[] {String.valueOf(partyId)},
        null);
    }

    public void onLoadFinished(Loader<Cursor> loader, Cursor data){
      libraryAdapter.swapCursor(data);
      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }

    public void onLoaderReset(Loader<Cursor> loader){
      libraryAdapter.swapCursor(null);
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
        songName.setText(cursor.getString(cursor.getColumnIndex(UDJPartyProvider.SONG_COLUMN)));

        TextView artistName =
          (TextView)view.findViewById(R.id.libraryArtistName);
        artistName.setText(cursor.getString(cursor.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)));
       
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
        values.put(UDJPartyProvider.PLAYLIST_LIBRARY_ID_COLUMN,Integer.valueOf(libId) );
        getActivity().getContentResolver().insert(
          UDJPartyProvider.PLAYLIST_URI,
          values);
      }
   
    }  
   
  }
 
}
