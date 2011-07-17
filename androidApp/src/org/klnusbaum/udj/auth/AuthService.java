package org.klnusbaum.udj.auth;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

public class AuthService extends Service {
  private static final String LOGTAG = "AUTH_SERVICE";
  private Authenticator authenticator;

  @Override
  public void onCreate(){
    authenticator = new Authenticator(this);
  }

  @Override
  public IBinder onBind(Intent intent){
    return authenticator.getIBinder();
  }
}
