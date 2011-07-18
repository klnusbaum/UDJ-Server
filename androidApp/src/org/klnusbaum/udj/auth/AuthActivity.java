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

package org.klnusbaum.udj.auth;

import android.accounts.AccountAuthenticatorActivity;
import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.ProgressDialog;
import android.view.View;
import android.widget.EditText;
import android.os.Handler;
import android.os.Bundle;
import android.content.Intent;
import android.content.ContentResolver;
import android.content.DialogInterface;
import android.app.AlertDialog;
import android.app.Dialog;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.R;

public class AuthActivity extends AccountAuthenticatorActivity {
  public static final String CONFIRMCREDENTIALS_EXTRA="confirmCredentials";
  public static final String PASSWORD_EXTRA = "password";
  public static final String USERNAME_EXTRA = "username";
  public static final String AUTHOTKEN_TYPE_EXTRA="authtokenType";
  public static final int PROGRESS_DIALOG = 0;
  public static final int FAILED_DIALOG = 1;

  private Thread authThread;
  private final Handler messageHandler = new Handler();

  private EditText usernameEdit;
  private EditText passwordEdit;

  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    setContentView(R.layout.login);

    usernameEdit = (EditText) findViewById(R.id.usernameEdit);
    passwordEdit = (EditText) findViewById(R.id.passwordEdit);
  }

  protected Dialog onCreateDialog(int id) {
    switch(id){
    case PROGRESS_DIALOG:
      final ProgressDialog dialog = new ProgressDialog(this);
      dialog.setMessage(getText(R.string.authenticating));
      dialog.setIndeterminate(true);
      dialog.setCancelable(true);
      dialog.setOnCancelListener(new DialogInterface.OnCancelListener() {
        public void onCancel(DialogInterface dialog) {
          if(authThread != null) {
            authThread.interrupt();
            finish();
          }
        }
      });
      return dialog;
    case FAILED_DIALOG:
      AlertDialog.Builder builder = new AlertDialog.Builder(this);
      builder.setMessage("Bad username and/or password. Please try again")
        .setCancelable(false)
        .setPositiveButton("Ok", new DialogInterface.OnClickListener(){
           public void onClick(DialogInterface dialog, int id){
             dialog.dismiss();
           }
         });
       return builder.create();
     default:
       return null;
     }
  }

  public void preformLogin(View view){
    String username = usernameEdit.getText().toString(); 
    String password = passwordEdit.getText().toString();
    showDialog(PROGRESS_DIALOG); 
    authThread = ServerConnection.attemptAuth(
      username, password, messageHandler, AuthActivity.this);
  }

  public void onAuthResult(boolean result){
    dismissDialog(PROGRESS_DIALOG);
    if(result){
      finishLogin();
    }
    else{
      showDialog(FAILED_DIALOG);
    }
  }

  private void finishLogin(){
    String username = usernameEdit.getText().toString();
    String password = passwordEdit.getText().toString();
    final Account account = new Account(
      username,
      getString(R.string.account_type));
    AccountManager acManager = AccountManager.get(this);
    acManager.addAccountExplicitly(
      account, password, null);
    ContentResolver.setSyncAutomatically(account,
      getString(R.string.authority), true);

    final Intent intent = new Intent();
    intent.putExtra(AccountManager.KEY_ACCOUNT_NAME, username);
    intent.putExtra(
      AccountManager.KEY_ACCOUNT_TYPE, getString(R.string.account_type));
    intent.putExtra(AccountManager.KEY_AUTHTOKEN, password);
    setAccountAuthenticatorResult(intent.getExtras());
    setResult(RESULT_OK, intent);
    finish();
  }
}

