package org.klnusbaum.udj;

import android.app.TabActivity;
import android.os.Bundle;
import android.content.Intent;
import android.widget.TabHost;

public class MainActivity extends TabActivity{
  public void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    
    setContentView(R.layout.tablayout);

    //Resources res = getResources();
    TabHost tabHost = getTabHost();
    TabHost.TabSpec spec;
    Intent intent;

    intent = new Intent().setClass(this, PlaylistActivity.class);
    spec = tabHost.newTabSpec("playlist").setIndicator("Playlist").setContent(intent);
    tabHost.addTab(spec);

    intent = new Intent().setClass(this, LibraryActivity.class);
    spec = tabHost.newTabSpec("library").setIndicator("Library").setContent(intent);
    tabHost.addTab(spec);
    
    tabHost.setCurrentTab(0);
  }
}
