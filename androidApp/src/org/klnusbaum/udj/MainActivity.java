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
