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

import android.accounts.Account;
import android.accounts.AccountAuthenticatorActivity;
import android.accounts.AccountManager;
import android.content.ContentResolver;
import android.content.Intent;
import android.view.View;
import android.widget.EditText;
import android.os.Bundle;
import android.util.Log;

import org.klnusbaum.udj.R;


public class AuthActivity extends AccountAuthenticatorActivity{

  private static final String LOGID = "AuthActivity";
  public static final String USERNAME_EXTRA = "username";
  public static final String AUTHTOKEN_TYPE_EXTRA = "auth_token_type";
  public static final String UPDATE_CREDS_EXTRA = "update credentials";

  private String username;
  private String authTokenType;

  private boolean addingNewAccount;
  private boolean confirmingCreds;

  private EditText usernameEdit;
  private EditText passwordEdit;
  private AccountManager am;
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    am = AccountManager.get(this);
    final Intent intent = getIntent();
    this.username = intent.getStringExtra(USERNAME_EXTRA);
    this.authTokenType = intent.getStringExtra(AUTHTOKEN_TYPE_EXTRA);
    addingNewAccount = (username == null); 
    confirmingCreds = intent.getBooleanExtra(UPDATE_CREDS_EXTRA, false);
    setContentView(R.layout.login);

    usernameEdit = (EditText) findViewById(R.id.usernameEdit);
    passwordEdit = (EditText) findViewById(R.id.passwordEdit);

    usernameEdit.setText(username);
   
  } 
     
  public void preformLogin(View view){
    Log.i(LOGID, "In preform login");
    if(addingNewAccount){
      username = usernameEdit.getText().toString();
    }
    String password = passwordEdit.getText().toString();
    //TODO throw error is password is blank
    
    //TODO Acutually preform login stuff
    final Account account = 
      new Account(username, "org.klnusbaum.udj");
    final Intent resultIntent = new Intent();
    if(addingNewAccount){
      Log.i(LOGID, "Before actual add");
      am.addAccountExplicitly(account, password, null);
      Log.i(LOGID, "after actual add");
      ContentResolver.setSyncAutomatically(account, 
        getString(R.string.authority), true);
      resultIntent.putExtra(AccountManager.KEY_ACCOUNT_NAME, username);
      resultIntent.putExtra(AccountManager.KEY_ACCOUNT_TYPE, 
        getString(R.string.account_type));
      if(authTokenType != null &&
        authTokenType.equals(getString(R.string.authtoken_type)))
      {
        resultIntent.putExtra(AccountManager.KEY_AUTHTOKEN, password);
      }
    }
    else{
      am.setPassword(account, password);
      resultIntent.putExtra(AccountManager.KEY_BOOLEAN_RESULT, true);
    } 
    AccountManager.get(this).setPassword(account, password);
    setAccountAuthenticatorResult(resultIntent.getExtras());
    setResult(RESULT_OK, resultIntent);
    Log.i(LOGID, "Before finish");
    finish();
  }
}
