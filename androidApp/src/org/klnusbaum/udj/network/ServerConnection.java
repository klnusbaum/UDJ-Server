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
package org.klnusbaum.udj.network;

import android.content.Context;
import android.os.Handler;

import org.klnusbaum.udj.auth.AuthActivity;

/**
 * A connection to the UDJ server
 */
public class ServerConnection{

  /**
   * Attempts to authenticate with ther UDJ server. Should
   * be used by the AuthActivity.
   *
   * @param username The user name to be authenticated.
   * @param password The password to be authenticated.
   * @param messageHandler A handler used to send messages back to the
   * AuthActivity that called attemptAuth.
   * @param context The context from which the method was called, i.e. the
   * AuthActivity.
   * @return A thread that is running the authentication attempt.
   */
  public static Thread attemptAuth(final String username, final String password,
    final Handler messageHandler, final Context context)
  {
    final Thread t = new Thread(){
      public void run(){
        authenticate(username, password, messageHandler, context);
      }
    };
    t.start();
    return t;
  }


  /**
   * Actually handles authenticating the the user.
   *
   * @param username The user name to be authenticated.
   * @param password The password to be authenticated.
   * @param messageHandler A handler used to send messages back to the
   * AuthActivity that called attemptAuth.
   * @param context The context from which the method was called, i.e. the
   * AuthActivity.
   * @return True if the authentication was successful. False otherwise.
   */
  public static boolean authenticate(String username, String password,
    Handler handler, final Context context)
  {
/*    handler.post(new Runnable(){
      public void run(){
        ((AuthActivity) context).onAuthResult(true);
      }
    });*/
    return true;
  }

  public static List<PlaylistEntry> syncPlaylist(Account account,
    String authtoken, GregorianCalendar lastUpdated)
  {
    return null;
  }

  public static List<LibraryEntry> syncLibrary(Account account,
    String authtoken, GregorianCalendar lastUpdated)
  {
    return null;
  }
}
