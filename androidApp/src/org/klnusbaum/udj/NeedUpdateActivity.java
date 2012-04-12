package org.klnusbaum.udj;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.content.Intent;
import android.net.Uri;

public class NeedUpdateActivity extends Activity{

  @Override
  public void onCreate(Bundle icicle){
    super.onCreate(icicle);
    setContentView(R.layout.needsupdate);
  }

  public void openMarket(View view){
    Intent openUdjInMarket = new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=org.klnusbaum.udj"));
    startActivity(openUdjInMarket);
  }

}
