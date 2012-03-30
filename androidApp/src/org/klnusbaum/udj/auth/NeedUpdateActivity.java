package org.klnusbaum.udj.auth;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.net.Uri;

import org.klnusbaum.udj.R;

public class NeedUpdateActivity extends Activity{

  @Override
  protected void onCreate(Bundle icicle){
    super.onCreate(icicle);
    setContentView(R.layout.needsupdate);
  }

  private void goToMarket(){
    Intent launchMarket = new Intent(
      Intent.ACTION_VIEW,
      Uri.parse("market://details?id=org.klnusbaum.udj"));
    startActivity(launchMarket);
  }

}
