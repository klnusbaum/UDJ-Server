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

import android.app.Activity;
import android.os.Bundle;
import android.database.Cursor;
import android.content.ContentValues;
import android.content.ContentResolver;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.ImageButton;
import android.content.Context;
import android.view.LayoutInflater;
import android.util.Log;
import android.accounts.Account;


/**
 * An Activity which displays the results of a library search.
 */
public class LibrarySearchActivity extends FragmentActivity{

  public static final String SEARCH_QUERY_EXTRA = "search_query";
  private static final int LIB_SEARCH_LOADER_TAG = 0;
  private String searchQuery;

  
  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    searchQuery = null; 
    if(savedInstanceState != null){
      searchQuery = savedInstanceState.getString(SEARCH_QUERY_EXTRA);
    }
    else{
      searchQuery = getIntent().getStringExtra(SEARCH_QUERY_EXTRA);
    }

    if(searchQuery == null){
      //TODO throw some sort of error.
    }

    //TODO before calling fragment, to get ID and give that to it.
    FragmentManager fm = getSupportFragmentManager();
    if(fm.findFragmentById(android.R.id.content) == null){
      Bundle queryBundle = new Bundle();
      queryBundle.putString(SEARCH_QUERY_EXTRA, searchQuery);
      LibraryFragment list = new LibraryFragment();
      list.setArguments(queryBundle);
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }
  }

  public static class LibrarySearchFragment extends ListFragment
    implements LoaderManager.LoaderCallbacks<ArrayList<LibraryEntry>>
  {
    /** Adapter used to help display the contents of the library. */
    LibrarySearchAdapter searchAdapter;
    private String searchQuery;
    
    @Override
    public void onActivityCreated(Bundle savedInstanceState){
      super.onActivityCreated(savedInstanceState);
      searchQuery = null; 
      if(savedInstanceState != null){
        searchQuery = savedInstanceState.getString(SEARCH_QUERY_EXTRA);
      }
      else{
        Bundle args = getArguements();
        if(args != null){
          searchQuery = args.getString(SEARCH_QUERY_EXTRA);
        }
      }
  
      if(searchQuery == null){
          //TODO throw some sort of error.
      }

      setEmptyText(getActivity().getString(R.string.no_library_songs));
      //setHasOptionsMenu(true);

      searchAdapter = new LibrarySearchAdapter(getActivity());
      setListAdapter(searchAdapter);
      setListShown(false);
      Bundle loaderArgs = new Bundle();
      loaderArgs.putString(SEARCH_QUERY_EXTRA, searchQuery);
      getLoaderManager().initLoader(LIB_SEARCH_LOADER_TAG, loaderArgs, this);
    }


    public Loader<ArrayList<LibraryEntry>> onCreateLoader(int id, Bundle args){
      if(id = LIB_SEARCH_LOADER_TAG){
        String query = args.getString(LIB_SEARCH_LOADER_TAG);
        if(query == null){
          //TODO throw some sort of error
        }
        return new LibrarySearchLoader(query);
      }
      return null;
    }

    public void onLoadFinished(
      Loader<ArrayList<LibraryEntry>> loader,
      ArrayList<LibraryEntry> data)
    {
      searchAdapter = new LibrarySearchAdapter(getActivity(), data);
      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }

    public void onLoaderReset(Loader<Cursor> loader){
      searchAdapter = new LibrarySearchAdapter(getActivity());
    }


 /* 
      @Override
      public void bindView(View view, Context context, Cursor cursor){
        int libraryId = cursor.getInt(
          cursor.getColumnIndex(UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN));
       
        TextView songName =
          (TextView)view.findViewById(R.id.librarySongName);
        songName.setText(cursor.getString(
          cursor.getColumnIndex(UDJPartyProvider.SONG_COLUMN)));

        TextView artistName =
          (TextView)view.findViewById(R.id.libraryArtistName);
        artistName.setText(cursor.getString(
          cursor.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)));
       
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
        String serverLibId = view.getTag().toString(); 
        ContentValues values = new ContentValues();
        values.put(
          UDJPartyProvider.SERVER_LIBRARY_ID_COLUMN,
          Integer.valueOf(serverLibId) );
        getActivity().getContentResolver().insert(
          UDJPartyProvider.PLAYLIST_URI,
          values);
        Bundle syncParams = new Bundle();
        syncParams.putBoolean(SyncAdapter.PLAYLIST_SYNC_EXTRA, true);
        syncParams.putLong(Party.PARTY_ID_EXTRA, partyId);
        syncParams.putBoolean(ContentResolver.SYNC_EXTRAS_MANUAL, true);
        ContentResolver.requestSync(
          account, getString(R.string.authority), syncParams);
      }
    }  */
  }
}
