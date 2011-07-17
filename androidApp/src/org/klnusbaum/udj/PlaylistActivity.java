package org.klnusbaum.udj;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class PlaylistActivity extends Activity{
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);

    TextView textview = new TextView(this);
    textview.setText("Playlist View");
    setContentView(textview);
  }
}
