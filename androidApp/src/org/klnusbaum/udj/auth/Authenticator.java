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

import java.util.Calendar;
import java.io.IOException;

import org.apache.http.auth.AuthenticationException;

import android.content.SharedPreferences;
import android.accounts.AbstractAccountAuthenticator;
import android.accounts.Account;
import android.accounts.AccountAuthenticatorResponse;
import android.accounts.AccountManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;

import org.klnusbaum.udj.R;
import org.klnusbaum.udj.Constants;
import org.klnusbaum.udj.network.ServerConnection;

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
    //TODO actually implement this method
    return null;
  }

  @Override
  public Bundle editProperties(AccountAuthenticatorResponse response,
    String accountType)
  {
    throw new UnsupportedOperationException();
  }

  @Override
  public Bundle getAuthToken(AccountAuthenticatorResponse response,
    Account account, String authTokenType, Bundle loginOptions)
  {
    final AccountManager am = AccountManager.get(context);
    final String password = am.getPassword(account);
    if(password != null){
      try{
        final ServerConnection.AuthResult authResult= 
          ServerConnection.authenticate(account.name, password);
        if(!TextUtils.isEmpty(authResult.ticketHash)) {
          am.setUserData(
            account, Constants.USER_ID_DATA, Long.toString(authResult.userId));
          return bundleUpAuthToken(account, authResult.ticketHash);
        }
      }
      catch(AuthenticationException e){
        //TODO actually do something with this exception 
      }
      catch(IOException e){
        //TODO actually do something with this exception 
      }
    }
    
    //Oh snap, they're username and password didn't work. O well, better have
    // them sort it out.
    final Intent intent = new Intent(context, AuthActivity.class);
    intent.putExtra(AuthActivity.PARAM_USERNAME, account.name);
    intent.putExtra(AuthActivity.PARAM_AUTHTOKEN_TYPE, authTokenType);
    intent.putExtra(AccountManager.KEY_ACCOUNT_AUTHENTICATOR_RESPONSE, 
      response);
    final Bundle bundle = new Bundle();
    bundle.putParcelable(AccountManager.KEY_INTENT, intent);
    return bundle;
  }

  private Bundle bundleUpAuthToken(Account account, String authToken){
    final Bundle result = new Bundle();
    result.putString(AccountManager.KEY_ACCOUNT_NAME, account.name);
    result.putString(AccountManager.KEY_ACCOUNT_TYPE, Constants.ACCOUNT_TYPE);
    result.putString(AccountManager.KEY_AUTHTOKEN, authToken);
    return result;
  }

  @Override
  public String getAuthTokenLabel(String authTokenType){
    // null means we don't support multiple authToken types
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
    return null;
  }
}
