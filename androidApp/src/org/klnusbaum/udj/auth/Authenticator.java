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

import android.accounts.AbstractAccountAuthenticator;
import android.accounts.Account;
import android.accounts.AccountAuthenticatorResponse;
import android.accounts.AccountManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

import org.klnusbaum.udj.R;

/**
 * Class used to authenticate with the UDJ server
 */
public class Authenticator extends AbstractAccountAuthenticator{

  private Context context;
  
  /**
   * Constructs an Authenticator
   *
   * @param context The context in which the Authenticator is
   * being used.
   */
  public Authenticator(Context context){
    super(context);
    this.context = context;
  }

  @Override
  public Bundle addAccount(AccountAuthenticatorResponse response,
    String accountType, String authTokenType, String[] requiredFeatures,
    Bundle options)
  {
    final Intent addIntent = new Intent(context, AuthActivity.class);
    addIntent.putExtra(AuthActivity.AUTHTOKEN_TYPE_EXTRA, authTokenType);
    addIntent.putExtra(AccountManager.KEY_ACCOUNT_AUTHENTICATOR_RESPONSE,
      response);
    final Bundle addBundle = new Bundle();
    addBundle.putParcelable(AccountManager.KEY_INTENT, addIntent);
    return addBundle;
  }

  @Override
  public Bundle confirmCredentials(AccountAuthenticatorResponse response,
    Account account, Bundle options)
  {
    //TOD actually implement this method
    final Bundle result = new Bundle();
    result.putBoolean(AccountManager.KEY_BOOLEAN_RESULT, true);
    return result;
  }

  @Override
  public Bundle editProperties(AccountAuthenticatorResponse response,
    String accountType)
  {
    throw new UnsupportedOperationException();
  }

  @Override
  public Bundle getAuthToken(AccountAuthenticatorResponse respones,
    Account account, String authTokenType, Bundle loginOptions)
  {
    if(!authTokenType.equals(context.getString(R.string.authtoken_type))){
      final Bundle result = new Bundle();
      result.putString(AccountManager.KEY_ERROR_MESSAGE,
        "Authtoken type not appropriate for this Authenticator!");
      return result;
    }
    final AccountManager am = AccountManager.get(context);
    final String password = am.getPassword(account);
    if(password != null){
      if(isValidUserNameAndPassword(account.name, password)){
        final Bundle result = new Bundle();
        result.putString(AccountManager.KEY_ACCOUNT_NAME, account.name);
        result.putString(AccountManager.KEY_ACCOUNT_TYPE, 
          context.getString(R.string.account_type));
        result.putString(AccountManager.KEY_AUTHTOKEN, password);
        return result;
      }
    }
    
    //TODO Doesn't get here yet, but if it does we need to launch the
    //AUTH_ACTIVITY and get the correct password.
    final Bundle result = new Bundle();
    result.putString(AccountManager.KEY_ACCOUNT_NAME, account.name);
    result.putString(AccountManager.KEY_ACCOUNT_TYPE, 
      context.getString(R.string.account_type));
    result.putString(AccountManager.KEY_AUTHTOKEN, "steve");
    return result;
  }

  @Override
  public String getAuthTokenLabel(String authTokenType){
    if(authTokenType.equals(context.getString(R.string.authtoken_type))){
      return context.getString(R.string.auth_token_label);
    }
    return null;
  }

  @Override
  public Bundle hasFeatures(AccountAuthenticatorResponse response,
    Account account, String[] freaturs)
  {
    final Bundle result = new Bundle();
    result.putBoolean(AccountManager.KEY_BOOLEAN_RESULT, false);
    return result;
  }

  @Override
  public Bundle updateCredentials(AccountAuthenticatorResponse response,
    Account account, String authTokenType, Bundle loginOptions)
  {
    final Intent updateIntent = new Intent(context, AuthActivity.class);
    updateIntent.putExtra(AuthActivity.USERNAME_EXTRA, account.name);
    updateIntent.putExtra(AuthActivity.AUTHTOKEN_TYPE_EXTRA, authTokenType);
    updateIntent.putExtra(AuthActivity.UPDATE_CREDS_EXTRA, true);
    final Bundle updateBundle = new Bundle();
    updateBundle.putParcelable(AccountManager.KEY_INTENT, updateIntent);
    return updateBundle;
  }
    
  /**
   * Determines whether or not the given username and password
   * combination are valid.
   *
   * @param username The username in question.
   * @param password The password assocaited with the username
   * in question.
   */ 
  private boolean isValidUserNameAndPassword(String username,
    String password)
  {
    //TODO Implement this function
    return true;
  }
}
