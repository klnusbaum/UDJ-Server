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

import org.klnusbaum.udj.PullToRefresh.RefreshableListFragment;

import android.accounts.Account;
import android.os.Bundle;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.Loader;

public abstract class SearchFragment extends RefreshableListFragment
  implements LoaderManager.LoaderCallbacks<MusicSearchLoader.MusicSearchResult>
{
  public static final int LIB_SEARCH_LOADER_TAG = 0;

  /** Adapter used to help display the contents of the library. */
  private MusicSearchAdapter searchAdapter;
  private Account account;

  @Override
  public void onActivityCreated(Bundle savedInstanceState){
    super.onActivityCreated(savedInstanceState);

    account = Utils.basicGetUdjAccount(getActivity());
    setEmptyText(getActivity().getString(R.string.no_library_songs));

    searchAdapter = new MusicSearchAdapter(getActivity(), account);
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

  @Override
	protected void doRefreshWork() {
	  getLoaderManager().restartLoader(LIB_SEARCH_LOADER_TAG, null, this);
  }
  
  public void onLoadFinished(
    Loader<MusicSearchLoader.MusicSearchResult> loader,
    MusicSearchLoader.MusicSearchResult data)
  {
	 refreshDone();
    if(data.getError() == MusicSearchLoader.MusicSearchError.NO_ERROR){
      searchAdapter = new MusicSearchAdapter(
        getActivity(),
        data.getResults(),
        account);
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
