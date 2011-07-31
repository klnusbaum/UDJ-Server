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
import android.widget.CursorAdapter;
import android.os.Bundle;
import android.database.Cursor;
import android.content.Context;
import android.view.View;
import android.widget.TextView;
import android.widget.ImageButton;
import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.util.Log;


import org.klnusbaum.udj.R;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PlaylistActivity extends ListActivity{

  /**
   * Adapter used to help display the contents of the playlist.
   */
  PlaylistAdapter playlistAdapter;

  @Override
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    Cursor playlistCursor = managedQuery(
      UDJPartyProvider.PLAYLIST_URI, null, null, null, null); 
    playlistAdapter = new PlaylistAdapter(this, playlistCursor);
    setListAdapter(playlistAdapter);
  }

  private class PlaylistAdapter extends CursorAdapter{
  
    public PlaylistAdapter(Context context, Cursor c){
      super(context, c);
    }

    @Override
    public void bindView(View view, Context context, Cursor cursor){
      
      int playlistId = cursor.getInt(cursor.getColumnIndex(UDJPartyProvider.PLAYLIST_ID_COLUMN));

      TextView songName = 
        (TextView)view.findViewById(R.id.playlistSongName);
      songName.setText(cursor.getString(cursor.getColumnIndex(UDJPartyProvider.SONG_COLUMN)));

      TextView artist = 
        (TextView)view.findViewById(R.id.playlistArtistName);
      artist.setText(cursor.getString(cursor.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)));
      if(cursor.getString(cursor.getColumnIndex(UDJPartyProvider.ARTIST_COLUMN)) == ""){
        Log.i("Playslist", "Didn't get artist");
      }

      ImageButton upVote = 
        (ImageButton)view.findViewById(R.id.up_vote_button);
      upVote.setTag(String.valueOf(playlistId));

      ImageButton downVote = 
        (ImageButton)view.findViewById(R.id.up_vote_button);
      downVote.setTag(String.valueOf(playlistId));

      String voteStatus = cursor.getString(cursor.getColumnIndex(UDJPartyProvider.VOTE_STATUS_COLUMN));
      if(voteStatus == UDJPartyProvider.VOTED_UP){
        upVote.setEnabled(false); 
      }
      else if(voteStatus == UDJPartyProvider.VOTED_DOWN){
        downVote.setEnabled(false); 
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
      bindView(itemView, context, cursor);
      return itemView;
    }
  }
}


