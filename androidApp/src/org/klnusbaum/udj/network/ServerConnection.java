package org.klnusbaum.udj.network;
import android.content.Context;
import android.os.Handler;

import org.klnusbaum.udj.auth.AuthActivity;

public class ServerConnection{

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


  public static boolean authenticate(String username, String password,
    Handler handler, final Context context)
  {
    handler.post(new Runnable(){
      public void run(){
        ((AuthActivity) context).onAuthResult(true);
      }
    });
    return true;
  }
}
