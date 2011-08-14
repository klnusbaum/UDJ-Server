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
import android.content.Context;
import android.view.View;
import android.widget.TextView;
import android.widget.ImageButton;
import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.util.Log;
import android.content.ContentValues;


import org.klnusbaum.udj.R;
import org.klnusbaum.udj.containers.Party;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PlaylistActivity extends FragmentActivity{

  private long partyId;

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
      PlaylistFragment list = new PlaylistFragment();
      list.setArguments(partyBundle);
      fm.beginTransaction().add(android.R.id.content, list).commit();
    }

  }

  public static class PlaylistFragment extends ListFragment
    implements LoaderManager.LoaderCallbacks<Cursor>
  {

    private static final int CURSOR_LOADER_ID = 0;

    private long partyId;
    /**
     * Adapter used to help display the contents of the playlist.
     */
    PlaylistAdapter playlistAdapter;

    @Override
    public void onActivityCreated(Bundle savedInstanceState){
      super.onActivityCreated(savedInstanceState);
      setEmptyText(getActivity().getString(R.string.no_playlist_items));
      //TODO throw some kind of error if the party id is null. Although it never should be.
      Bundle args = getArguements();
      if(args.containsKey(PartyActivity.PARTY_ID_EXTRA)){
        partyId = args.getLong(PartyActivity.PARTY_ID_EXTRA);
      }
      else{
        getActivity().setResult(Activity.RESULT_CANCELED);
        getActivity().finish();
      }

      //setHasOptionsMenu(true)
      playlistAdapter = new PlaylistAdapter(getActivity(), null);
      setListAdapter(playlistAdapter);
      setListShown(false);
      getLoaderManager().initLoader(CURSOR_LOADER_ID, null, this);
    }
    

    public Loader<Cursor> onCreateLoader(int id, Bundle args){
      return new CursorLoader(
        getActivity(), 
        UDJPartyProvider.PLAYLIST_URI, 
        null,
        "partyId=?",
        new String[] {String.valueOf(partyId)},
        null);
    }

    public void onLoadFinished(Loader<Cursor> loader, Cursor data){
      playlistAdapter.swapCursor(data);
      if(isResumed()){
        setListShown(true);
      }
      else if(isVisible()){
        setListShownNoAnimation(true);
      }
    }

    public void onLoaderReset(Loader<Cursor> loader){
      playlistAdapter.swapCursor(null);
    }

    private class PlaylistAdapter extends CursorAdapter{
  
      public PlaylistAdapter(Context context, Cursor c){
        super(context, c);
      }

      @Override
      public void bindView(View view, Context context, Cursor cursor){
        int playlistId = cursor.getInt(cursor.getColumnIndex(
          UDJPartyProvider.PLAYLIST_ID_COLUMN));
  
        TextView songName = 
          (TextView)view.findViewById(R.id.playlistSongName);
        songName.setText(cursor.getString(cursor.getColumnIndex(
          UDJPartyProvider.SONG_COLUMN)));
  
        TextView artist = 
          (TextView)view.findViewById(R.id.playlistArtistName);
        artist.setText(cursor.getString(cursor.getColumnIndex(
          UDJPartyProvider.ARTIST_COLUMN)));
  
        ImageButton upVote = 
          (ImageButton)view.findViewById(R.id.up_vote_button);
        upVote.setTag(String.valueOf(playlistId));
        upVote.setOnClickListener(new View.OnClickListener(){
          public void onClick(View v){
            upVoteClick(v);
          }
        });
  
        ImageButton downVote = 
          (ImageButton)view.findViewById(R.id.down_vote_button);
        downVote.setTag(String.valueOf(playlistId));
        downVote.setOnClickListener(new View.OnClickListener(){
          public void onClick(View v){
            downVoteClick(v);
          }
        });
  
        String voteStatus = cursor.getString(cursor.getColumnIndex(
          UDJPartyProvider.VOTE_STATUS_COLUMN));
        if(voteStatus.equals(UDJPartyProvider.VOTED_UP)){
          upVote.setEnabled(false); 
        }
        else{
          upVote.setEnabled(true);
        } 
  
        if(voteStatus.equals(UDJPartyProvider.VOTED_DOWN)){
          downVote.setEnabled(false); 
        }
        else{
          downVote.setEnabled(true);
        }
  
        TextView votes = 
          (TextView)view.findViewById(R.id.playlistVotes);
        votes.setText(String.valueOf(
        cursor.getInt(cursor.getColumnIndex(UDJPartyProvider.VOTES_COLUMN))));
        
      }
  
      @Override
      public View newView(Context context, Cursor cursor, ViewGroup parent){
        LayoutInflater inflater = (LayoutInflater)context.getSystemService(
          Context.LAYOUT_INFLATER_SERVICE);
        View itemView = inflater.inflate(R.layout.playlist_list_item, null);
        return itemView;
      }
  
      private void upVoteClick(View view){
        String playlistId = view.getTag().toString();
        ContentValues toUpdate = new ContentValues();
        toUpdate.put(
          UDJPartyProvider.VOTE_STATUS_COLUMN, UDJPartyProvider.VOTED_UP);
        toUpdate.put(
          UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.NEEDS_UP_VOTE);
        getActivity().getContentResolver().update(
          UDJPartyProvider.PLAYLIST_URI,
          toUpdate,
          UDJPartyProvider.PLAYLIST_ID_COLUMN + "= ?",
          new String[]{playlistId});
      }
    
      private void downVoteClick(View view){
        String playlistId = view.getTag().toString();
        ContentValues toUpdate = new ContentValues();
        toUpdate.put(
          UDJPartyProvider.VOTE_STATUS_COLUMN, UDJPartyProvider.VOTED_DOWN);
        toUpdate.put(
          UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.NEEDS_DOWN_VOTE);
        getActivity().getContentResolver().update(
          UDJPartyProvider.PLAYLIST_URI,
        toUpdate,
        UDJPartyProvider.PLAYLIST_ID_COLUMN + "= ?",
        new String[]{playlistId});
      }
    }
  }
}


