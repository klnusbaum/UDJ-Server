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
import android.support.v4.content.Loader;

import android.os.Bundle;
import android.content.Intent;
import android.content.ContentValues;
import android.content.ContentResolver;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.view.View;

import org.klnusbaum.udj.network.PlaylistSyncService;
import org.klnusbaum.udj.containers.LibraryEntry;

public abstract class SearchFragment extends ListFragment
  implements LoaderManager.LoaderCallbacks<MusicSearchLoader.MusicSearchResult>
{
  public static final int LIB_SEARCH_LOADER_TAG = 0;

  /** Adapter used to help display the contents of the library. */
  private MusicSearchAdapter searchAdapter;
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

    account = Utils.basicGetUdjAccount(getActivity());
    setEmptyText(getActivity().getString(R.string.no_library_songs));

    searchAdapter = new MusicSearchAdapter(getActivity());
    setListAdapter(searchAdapter);
    setListShown(false);
    getLoaderManager().initLoader(LIB_SEARCH_LOADER_TAG, null, this);
  }

  public Loader<MusicSearchLoader.MusicSearchResult> onCreateLoader(
    int id, Bundle args)
  {
    if(id == LIB_SEARCH_LOADER_TAG){
      return getLoader(account);
    }
    return null;
  }

  public void onLoadFinished(
    Loader<MusicSearchLoader.MusicSearchResult> loader,
    MusicSearchLoader.MusicSearchResult data)
  {
    if(data.getError() == MusicSearchLoader.MusicSearchError.NO_ERROR){
      searchAdapter = new MusicSearchAdapter(
        getActivity(),
        data.getResults(),
        addSongToPlaylistListener);
      setListAdapter(searchAdapter);
    }
    else if(data.getError() ==
      MusicSearchLoader.MusicSearchError.EVENT_ENDED_ERROR)
    {
      Utils.handleEventOver(getActivity(), account);
    }

    if(isResumed()){
      setListShown(true);
    }
    else if(isVisible()){
      setListShownNoAnimation(true);
    }
  }

  public void onLoaderReset(Loader<MusicSearchLoader.MusicSearchResult> loader){
    setListAdapter(null);
  }

  protected abstract Loader<MusicSearchLoader.MusicSearchResult> getLoader(Account account);


}
