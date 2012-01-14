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

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.content.IntentFilter;
import android.widget.TabHost;
import android.widget.Toast;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MenuInflater;
import android.view.View;
import android.widget.TextView;
import android.content.Context;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.DialogInterface;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.ContentResolver;
import android.util.Log;
import android.app.SearchManager;
import android.net.Uri;
import android.database.Cursor;
import android.view.Window;
import android.os.Build;
import android.content.BroadcastReceiver;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.DialogFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.CursorLoader;
import android.support.v4.content.Loader;

import java.util.HashMap;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.actionbar.ActionBarActivity;
import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.network.PlaylistSyncService;
import org.klnusbaum.udj.network.EventCommService;

/**
 * The main activity display class.
 */
public class EventActivity extends EventEndedListenerActivity
  implements LoaderManager.LoaderCallbacks<Cursor>
{
  private static final String QUIT_DIALOG_TAG = "quit_dialog";
  private static final int CURRENT_SONG_LOADER_ID = 1;
  private static final String TAG = "EventActivity";

  private TextView currentSong;

  @Override
  protected void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    if(Build.VERSION.SDK_INT < Build.VERSION_CODES.HONEYCOMB){ 
      requestWindowFeature(Window.FEATURE_NO_TITLE);
    }
    setContentView(R.layout.event);
    currentSong = (TextView)findViewById(R.id.current_song_title);
    setCurrentSongDisplay(null);
    //TODO hanle if no event
    getPlaylistFromServer();    
    getSupportLoaderManager().initLoader(CURRENT_SONG_LOADER_ID, null, this);
  }


  private void getPlaylistFromServer(){
    Intent getPlaylist = new Intent(
      Intent.ACTION_VIEW,
      UDJEventProvider.PLAYLIST_URI,
      this,
      PlaylistSyncService.class);
    getPlaylist.putExtra(Constants.ACCOUNT_EXTRA, account);
    startService(getPlaylist);
  } 

  public Loader<Cursor> onCreateLoader(int id, Bundle args){
    switch(id){
    case CURRENT_SONG_LOADER_ID:
      return new CursorLoader(
        this,
        UDJEventProvider.CURRENT_SONG_URI,
        new String[]{UDJEventProvider.TITLE_COLUMN},
        null,
        null,
        null);
    default:
      return null;
    }
  }

  public void onLoadFinished(Loader<Cursor> loader, Cursor data){
    if(loader.getId()==CURRENT_SONG_LOADER_ID){
      setCurrentSongDisplay(data);   
    }
  }

  public void onLoaderReset(Loader<Cursor> loader){
    
  }

  private void setCurrentSongDisplay(Cursor data){
    if(data != null && data.moveToFirst()){
      currentSong.setText(data.getString(data.getColumnIndex(
        UDJEventProvider.TITLE_COLUMN)));
    }
    else{
      currentSong.setText(R.string.no_current_song);
    }
  }

  public boolean onCreateOptionsMenu(Menu menu){
    MenuInflater inflater = getMenuInflater();
    inflater.inflate(R.menu.event, menu);
    return true;
  }

  public boolean onOptionsItemSelected(MenuItem item){
    switch (item.getItemId()) {
    case R.id.menu_refresh:
      getPlaylistFromServer();
      return true;
    case R.id.menu_search:
      startSearch(null, false, null, false);
      return true;  
    default:
      return super.onOptionsItemSelected(item);
    }
  }

  protected void onNewIntent(Intent intent){
    Log.d(TAG, "In on new intent");
    if(Intent.ACTION_SEARCH.equals(intent.getAction())){
      intent.setClass(this, MusicSearchActivity.class);
      startActivityForResult(intent, 0);
    }
  }

  @Override 
  public void onBackPressed(){
    DialogFragment newFrag = new QuitDialogFragment();
    newFrag.show(getSupportFragmentManager(), QUIT_DIALOG_TAG);
  }

  private void doQuit(){
    dismissQuitDialog();
    Intent leaveEvent = new Intent(
      Intent.ACTION_DELETE,
      Constants.EVENT_URI,
      this,
      EventCommService.class);
    leaveEvent.putExtra(Constants.ACCOUNT_EXTRA, account);
    startService(leaveEvent);
    setResult(Activity.RESULT_OK);
    finish();
  }

  private void dismissQuitDialog(){
    QuitDialogFragment qd = 
      (QuitDialogFragment)getSupportFragmentManager().findFragmentByTag(QUIT_DIALOG_TAG);
    qd.dismiss();
  }

  public static class QuitDialogFragment extends DialogFragment{
    
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
      return new AlertDialog.Builder(getActivity())
        .setTitle(R.string.quit_title)
        .setMessage(R.string.quit_message)
        .setPositiveButton(android.R.string.ok,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              ((EventActivity)getActivity()).doQuit();
            }
          })
        .setNegativeButton(android.R.string.cancel,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              ((EventActivity)getActivity()).dismissQuitDialog();
            }
          })
        .create();
    }
  }
}
