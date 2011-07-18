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
