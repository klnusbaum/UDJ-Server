package org.klnusbaum.udj.auth;

import android.accounts.AbstractAccountAuthenticator;
import android.accounts.Account;
import android.accounts.AccountAuthenticatorResponse;
import android.accounts.AccountManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

class Authenticator extends AbstractAccountAuthenticator{

  Context context;
  public Authenticator(Context context){
    super(context);
    this.context= context; 
  }

  public Bundle addAccount(AccountAuthenticatorResponse response,
    String accountType, String authTokenType, String[] requiredFeatures,
    Bundle options) throws NetworkErrorException
  {
    final Intent intent = net Intent(mContext, AuthActivity.class);
    intent.putExtra(AuthActivity.AUTHTOKEN_TYPE_EXTRA, authTokenType);
    intent.putExtra(AccountManager.KEY_ACCOUNT_AUTHENTICATOR_RESPONSE,
      response);
    final Bundle bundle = new Bundle();
    bundle.putParcelable(AccountManager.KEY_INTENT, intent);
    return bundle;
  }

  public Bundle confirmCredentials(AccountAuthenticatorResponse response,
    Account account, Bundle options) 
  {
    if(options != null && options.containsKey(AccountManager.KEY_PASSWORD)){
      final String password = options.getString(AccountManager.KEY_PASSWORD);
      final verified = serverConfirmPassword(account.name, password);
      final Bundle result = new Bundle();
      result.putBoolean(AccountManager.KEY_BOOLEAN_RESULT, verified);
      return result;
    }
  }

  public Bundle editProperties(AccountAuthenticatorResponse response,
    String accountType)
  {
    return null;
  }

  public Bundle getAuthToken(AccountAuthenticatorResponse response,
    Account account, String authTokenType, Bundle loginOptions)
  {
    return null;
  }

  public String getAuthTokenLabel(String authTokenType){
    return null;
  }

  public Bundle hasFeatures(AccountAuthenticatorResponse response,
    Account account, String[] freatures)
  {
    return null;
  }

  public Bundle updateCredentials(AccountAuthenticatorResponse response,
    Account account, String authTokenType, Bundle loginOptions)
  {
    return null;
  }

}


