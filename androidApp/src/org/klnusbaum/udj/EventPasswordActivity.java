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
import android.view.View;
import android.widget.EditText;
import android.content.Context;
import android.util.Log;

import org.klnusbaum.udj.containers.Event;

public class EventPasswordActivity extends Activity{

  Event toJoin;
  EditText passwordEdit;

  protected void onCreate(Bundle icicle){
    super.onCreate(icicle);
    setContentView(R.layout.event_password);
    toJoin = Event.unbundle(getIntent().getBundleExtra(Constants.EVENT_EXTRA));
    //setTitle(getString(R.string.event_label) + " " + toJoin.getName());
    passwordEdit = (EditText)findViewById(R.id.event_password_edit);
  }

  public void handleLoginToEvent(View view){
    //TODO handle if they didn't type anything in
    Intent toReturn = new Intent();
    String password = passwordEdit.getText().toString();
    toReturn.putExtra(Constants.EVENT_EXTRA, toJoin.bundleUp());
    toReturn.putExtra(Constants.EVENT_PASSWORD_EXTRA, password);
    setResult(Activity.RESULT_OK, toReturn);
    finish();
  }

}

