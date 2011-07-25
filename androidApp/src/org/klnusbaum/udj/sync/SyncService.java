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
package org.klnusbaum.udj.sync;


import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

/**
 * Service used to help sync data with the udj server.
 */
public class SyncService extends Service{

  private static final Object syncAdapterLock = new Object();
  private static SyncAdapter syncAdapter = null;

  @Override
  public void onCreate(){
    synchronized(syncAdapterLock){
      if(syncAdapter == null){
        syncAdapter = new SyncAdapter(getApplicationContext(), true);
      }
    }
  }

  @Override
  public IBinder onBind(Intent intent){
    return syncAdapter.getSyncAdapterBinder();
  }
}
