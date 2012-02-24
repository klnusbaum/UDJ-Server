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

import android.os.Bundle;
import android.content.Intent;
import android.database.Cursor;
import android.content.Context;
import android.content.ContentResolver;
import android.view.View;
import android.widget.TextView;
import android.widget.ImageButton;
import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.util.Log;
import android.content.ContentValues;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.widget.AdapterView;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.ContextMenu;
import android.widget.ListView;
import android.widget.RelativeLayout;

import org.klnusbaum.udj.network.PlaylistSyncService;
import org.klnusbaum.udj.containers.Event;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PlaylistFragment extends ListFragment
  implements LoaderManager.LoaderCallbacks<Cursor>
{
  private static final String TAG = "PlaylistFragment";
  private static final int PLAYLIST_LOADER_ID = 0;
  private Account account;
  private long userId;
  private AccountManager am;
  /**
   * Adapter used to help display the contents of the playlist.
   */
  PlaylistAdapter playlistAdapter;

  @Override
  public void onActivityCreated(Bundle savedInstanceState){
    super.onActivityCreated(savedInstanceState);
    account = Utils.basicGetUdjAccount(getActivity());
    am = AccountManager.get(getActivity());
    userId = Long.valueOf(am.getUserData(account, Constants.USER_ID_DATA));
    setEmptyText(getActivity().getString(R.string.no_playlist_items));
    playlistAdapter = new PlaylistAdapter(getActivity(), null, userId);
    setListAdapter(playlistAdapter);
    setListShown(false);
    getLoaderManager().initLoader(PLAYLIST_LOADER_ID, null, this);
    registerForContextMenu(getListView());
  }

  public void onListItemClick(ListView l, View v, int position, long id){
    l.showContextMenuForChild(v);
  }

  @Override
	public void onCreateContextMenu(ContextMenu menu, View v, 
		ContextMenu.ContextMenuInfo menuInfo)
  {
    AdapterView.AdapterContextMenuInfo info = 
      (AdapterView.AdapterContextMenuInfo)menuInfo;
    Cursor song = (Cursor)playlistAdapter.getItem(info.position); 
    MenuInflater inflater = getActivity().getMenuInflater();
    inflater.inflate(R.menu.playlist_context, menu);
    if(
      song.getLong(song.getColumnIndex(UDJEventProvider.ADDER_ID_COLUMN))
      ==
      userId 
    )
    {
      menu.findItem(R.id.vote_up).setEnabled(false);
      menu.findItem(R.id.vote_down).setEnabled(false);
    }
    else if(!song.isNull(
      song.getColumnIndex(UDJEventProvider.VOTE_TYPE_COLUMN)))
    {
      int voteType = song.getInt(
          song.getColumnIndex(UDJEventProvider.VOTE_TYPE_COLUMN));
      if(voteType == UDJEventProvider.UP_VOTE_TYPE){
        menu.findItem(R.id.vote_up).setEnabled(false);
        menu.findItem(R.id.remove_song).setEnabled(false);
      }
      else{
        menu.findItem(R.id.vote_down).setEnabled(false);
        menu.findItem(R.id.remove_song).setEnabled(false);
      }
    }
    else{
      menu.findItem(R.id.remove_song).setEnabled(false);
    }
    int titleIndex = 
      song.getColumnIndex(UDJEventProvider.TITLE_COLUMN);
    menu.setHeaderTitle(song.getString(titleIndex));
  }

	@Override
	public boolean onContextItemSelected(MenuItem item){
    AdapterView.AdapterContextMenuInfo info = 
      (AdapterView.AdapterContextMenuInfo)item.getMenuInfo();
    switch(item.getItemId()){
    case R.id.share:
      shareSong(info.position);
			return true;
    case R.id.vote_up:
      upVoteSong(info.position); 
      return true;
    case R.id.vote_down:
      downVoteSong(info.position); 
      return true;
		default:
			return super.onContextItemSelected(item);
		}
	}

  private void shareSong(int position){
    Cursor toShare = (Cursor)playlistAdapter.getItem(position); 
    int titleIndex = 
      toShare.getColumnIndex(UDJEventProvider.TITLE_COLUMN);
    String songTitle = toShare.getString(titleIndex);
    String eventName = am.getUserData(account, Constants.EVENT_NAME_DATA);
    Intent shareIntent = new Intent(Intent.ACTION_SEND);
		shareIntent.setType("text/plain");
		shareIntent.putExtra(
			android.content.Intent.EXTRA_TEXT, 
			getString(R.string.song_share_1) + " " + 
			songTitle + " " +
			getString(R.string.song_share_2) + " " + eventName + ".");
		startActivity(
			Intent.createChooser(shareIntent, getString(R.string.share_via)));

  }

  private void upVoteSong(int position){
    voteOnSong(position, UDJEventProvider.UP_VOTE_TYPE);
  }
  
  private void downVoteSong(int position){
    voteOnSong(position, UDJEventProvider.DOWN_VOTE_TYPE);
  }

  private void voteOnSong(int position, int voteType){
    Cursor song = (Cursor)playlistAdapter.getItem(position);
    int idIndex = song.getColumnIndex(UDJEventProvider.PLAYLIST_ID_COLUMN);
    long playlistId = song.getLong(idIndex);
    Intent voteIntent = new Intent(
      Intent.ACTION_INSERT,
      UDJEventProvider.VOTES_URI,
      getActivity(),
      PlaylistSyncService.class);
    voteIntent.putExtra(Constants.ACCOUNT_EXTRA, account);
    voteIntent.putExtra(Constants.VOTE_TYPE_EXTRA, voteType);
    voteIntent.putExtra(Constants.PLAYLIST_ID_EXTRA, playlistId);
    getActivity().startService(voteIntent);
  }

  public Loader<Cursor> onCreateLoader(int id, Bundle args){
    switch(id){
    case PLAYLIST_LOADER_ID:
      return new CursorLoader(
        getActivity(), 
        UDJEventProvider.PLAYLIST_URI, 
        null,
        null,
        null,
        UDJEventProvider.PRIORITY_COLUMN);
    default:
      return null;
    }
  }

  public void onLoadFinished(Loader<Cursor> loader, Cursor data){
    if(loader.getId()==PLAYLIST_LOADER_ID){
      playlistAdapter.swapCursor(data);
      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }
  }

  public void onLoaderReset(Loader<Cursor> loader){
    if(loader.getId()==PLAYLIST_LOADER_ID){
      playlistAdapter.swapCursor(null);
    }
  }

  private class PlaylistAdapter extends CursorAdapter{
    private long userId;
    private static final String PLAYLIST_ADAPTER_TAG = "PlaylistAdapter";
    public PlaylistAdapter(Context context, Cursor c, long userId){
      super(context, c);
      this.userId = userId;
    }

    @Override
    public void bindView(View view, Context context, Cursor cursor){
      int playlistIdIndex = 
        cursor.getColumnIndex(UDJEventProvider.PLAYLIST_ID_COLUMN);
      int playlistId = cursor.getInt(playlistIdIndex);

      TextView songName = (TextView)view.findViewById(R.id.playlistSongName);
      int titleIndex = cursor.getColumnIndex(UDJEventProvider.TITLE_COLUMN);
      songName.setText(cursor.getString(titleIndex));

      TextView artist = (TextView)view.findViewById(R.id.playlistArtistName);
      int artistIndex = cursor.getColumnIndex(UDJEventProvider.ARTIST_COLUMN);
      artist.setText(
        getString(R.string.by) + " " + cursor.getString(artistIndex));

      TextView addByUser = 
        (TextView)view.findViewById(R.id.playlistAddedBy);
      int adderIdIndex = 
        cursor.getColumnIndex(UDJEventProvider.ADDER_ID_COLUMN);
      if( cursor.getLong(adderIdIndex) == userId){
        addByUser.setText(
          getString(R.string.added_by) + " " + getString(R.string.you)); 
      }
      else{
        int adderUserNameIndex = 
          cursor.getColumnIndex(UDJEventProvider.ADDER_USERNAME_COLUMN);
        addByUser.setText(
          getString(R.string.added_by) + " " +
          cursor.getString(adderUserNameIndex));
      }
    }

    @Override
    public View newView(Context context, Cursor cursor, ViewGroup parent){
      LayoutInflater inflater = (LayoutInflater)context.getSystemService(
        Context.LAYOUT_INFLATER_SERVICE);
      View itemView = inflater.inflate(R.layout.playlist_list_item, null);
      return itemView;
    }

  }

}
