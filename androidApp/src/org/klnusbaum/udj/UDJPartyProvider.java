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

import android.content.ContentProvider;
import android.net.Uri;
import android.content.ContentValues;
import android.database.Cursor;

public class UDJPartyProvider extends ContentProvider{

  public boolean onCreate(){
    return true;
  }

  public String getType(Uri uri){
    return "none";
  }

  public int delete(Uri uri, String where, String[] whereArgs){
    return 0;
  }

  public Uri insert(Uri uri, ContentValues initialValues){
    return null;
  }
  
  public Cursor query(Uri uri, String[] projection, 
    String selection, String[] selectionArgs, String sortOrder)
  {
    return null;
  }

  public int update(Uri uri, ContentValues values, String where, 
    String[] whereArgs)
  {
    return 0;
  }

}
