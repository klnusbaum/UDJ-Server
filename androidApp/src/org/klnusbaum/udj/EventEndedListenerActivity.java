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
import android.content.Context;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.DialogInterface;
import android.app.Dialog;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.util.Log;
import android.os.Parcelable;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.DialogFragment;

import org.klnusbaum.udj.network.EventCommService;

public abstract class EventEndedListenerActivity extends FragmentActivity{

  private static final String EVENT_ENDED_DIALOG = "event_end_dialog";
  private static final String TAG = "EventEndedListenerActivity";
  private static final int HANDLED_EVENT_END_CODE = 0;
  protected Account account;

  private BroadcastReceiver eventEndedReciever = new BroadcastReceiver(){
    public void onReceive(Context context, Intent intent){
      Log.d(TAG, "Recieved event ended");
      unregisterReceiver(eventEndedReciever);
      eventEnded();
    }
  };

  protected void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    account = Utils.basicGetUdjAccount(this);
    int eventStatus = Integer.valueOf(AccountManager.get(this).getUserData(
      account, Constants.IN_EVENT_DATA));
    if(eventStatus == Constants.NOT_IN_EVENT_FLAG){
      finish();
      return;
    }
  }

  protected void onResume(){
    int inEvent = Integer.valueOf(
      AccountManager.get(this).getUserData(account, Constants.IN_EVENT_DATA));
    if(inEvent == Constants.NOT_IN_EVENT_FLAG){
      eventEnded();
    }
    else{
      registerReceiver(
        eventEndedReciever, 
        new IntentFilter(Constants.EVENT_ENDED_ACTION));
    }
    super.onResume();
  }

  protected void onPause(){
    super.onPause();
    try{
      unregisterReceiver(eventEndedReciever);
    }
    catch(IllegalArgumentException e){

    }
  }

  private void eventEnded(){
    Intent leaveEvent = new Intent(
      Intent.ACTION_DELETE,
      Constants.EVENT_URI,
      this,
      EventCommService.class);
    leaveEvent.putExtra(Constants.ACCOUNT_EXTRA, account);
    startService(leaveEvent);
    DialogFragment newFrag = new EventEndedDialog();
    newFrag.show(getSupportFragmentManager(), EVENT_ENDED_DIALOG);
  }

  protected void onActivityResult(int requestCode, int resultCode, Intent data){
    if(resultCode == HANDLED_EVENT_END_CODE){
      setResult(HANDLED_EVENT_END_CODE);
      finish();
    }
  }

  public static class EventEndedDialog extends DialogFragment{
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
      return new AlertDialog.Builder(getActivity())
        .setTitle(R.string.event_ended_title)
        .setMessage(R.string.event_ended_message)
        .setPositiveButton(android.R.string.ok,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              getActivity().setResult(HANDLED_EVENT_END_CODE);
              getActivity().finish();
            }
          })
        .setOnCancelListener(new DialogInterface.OnCancelListener(){
          public void onCancel(DialogInterface dialog){
            getActivity().setResult(HANDLED_EVENT_END_CODE);
            getActivity().finish();
          }
        })
        .create();
    }
  }
}
