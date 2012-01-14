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

import android.support.v4.app.ListFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.CursorLoader;
import android.support.v4.content.Loader;
import android.support.v4.widget.CursorAdapter;

import android.database.Cursor;
import android.os.Bundle;
import android.content.Intent;
import android.content.ContentValues;
import android.content.ContentResolver;
import android.accounts.Account;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.ImageButton;
import android.view.LayoutInflater;

import java.util.List;

import org.klnusbaum.udj.network.PlaylistSyncService;
import org.klnusbaum.udj.containers.LibraryEntry;

public class MusicSearchFragment extends ListFragment
  implements LoaderManager.LoaderCallbacks<List<LibraryEntry>>
{
  public static final String SEARCH_QUERY_EXTRA = "search_query";
  private static final int LIB_SEARCH_LOADER_TAG = 0;

  /** Adapter used to help display the contents of the library. */
  MusicSearchAdapter searchAdapter;
  private String searchQuery;
  private Account account;

  private View.OnClickListener addSongToPlaylistListener =
    new View.OnClickListener(){
      public void onClick(View v){
        LibraryEntry songToAdd = 
          (LibraryEntry)v.getTag(R.id.LIB_ENTRY_VIEW_TAG);
        Intent addSongIntent = new Intent(
          Intent.ACTION_INSERT,
          UDJEventProvider.PLAYLIST_ADD_REQUEST_URI,
          getActivity(),
          PlaylistSyncService.class);
        addSongIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
        addSongIntent.putExtra(Constants.LIB_ID_EXTRA, songToAdd.getLibId());
        getActivity().startService(addSongIntent);
      }
    };

  
  @Override
  public void onActivityCreated(Bundle savedInstanceState){
    super.onActivityCreated(savedInstanceState);

    setEmptyText(getActivity().getString(R.string.no_library_songs));
    //setHasOptionsMenu(true);
    Bundle args = getArguments();
    searchQuery = args.getString(SEARCH_QUERY_EXTRA);
    account = Utils.basicGetUdjAccount(getActivity());
    //TODO Hanle null account.

    searchAdapter = new MusicSearchAdapter(getActivity());
    setListAdapter(searchAdapter);
    setListShown(false);
    getLoaderManager().initLoader(LIB_SEARCH_LOADER_TAG, null, this);
  }

  public void setSearchQuery(String newQuery){
    searchQuery = newQuery;
    getLoaderManager().restartLoader(LIB_SEARCH_LOADER_TAG, null, this);
  }
    
  public Loader<List<LibraryEntry>> onCreateLoader(int id, Bundle args){
    if(id == LIB_SEARCH_LOADER_TAG){
      return new MusicSearchLoader(
        getActivity(), searchQuery, account);
    }
    return null;
  }

  public void onLoadFinished(
    Loader<List<LibraryEntry>> loader,
    List<LibraryEntry> data)
  {
    searchAdapter = new MusicSearchAdapter(
      getActivity(), 
      data,
      addSongToPlaylistListener);
    setListAdapter(searchAdapter);
    if(isResumed()){
      setListShown(true);
    }
    else if(isVisible()){
      setListShownNoAnimation(true);
    }
  }

  public void onLoaderReset(Loader<List<LibraryEntry>> loader){
    searchAdapter = new MusicSearchAdapter(getActivity());
  }
}
