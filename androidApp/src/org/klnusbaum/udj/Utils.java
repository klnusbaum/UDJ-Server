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

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.accounts.AccountManager;
import android.accounts.Account;

public class Utils{

  public static boolean isNetworkAvailable(Context context){
    ConnectivityManager cm = ((ConnectivityManager)context.getSystemService(
      Context.CONNECTIVITY_SERVICE));
    NetworkInfo info = cm.getActiveNetworkInfo();
    if(info != null && info.isConnected()){
      return true;
    }
    return false;
  }

  public static Account basicGetUdjAccount(Context context){
    AccountManager am = AccountManager.get(context);
    Account[] udjAccounts = am.getAccountsByType(Constants.ACCOUNT_TYPE);
    return udjAccounts[0];
  }

}
