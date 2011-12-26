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
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteQueryBuilder;
import android.content.Context;
import android.util.Log;
import android.database.SQLException;
import android.content.ContentUris;

import java.util.ArrayList;

/**
 * Content provider used to maintain the content asociated
 * with the current party the user is logged into.
 */
public class UDJPartyProvider extends ContentProvider{
  
	/** Name of the database */
  private static final String DATABASE_NAME = "partydb.db";
	/** Database version number */
  private static final int DATABASE_VERSION = 1;

  /** URI for the playlist */
  public static final Uri PLAYLIST_URI = 
    Uri.parse("content://org.klnusbaum.udj/playlist");

  public static final Uri PARTIERS_URI =
    Uri.parse("content://org.klnusbaum.udj/partiers");

  /** PLAYLIST TABLE */

	/** Name of the playlist table. */
  private static final String PLAYLIST_TABLE_NAME = "playlist";

	/** Constants used for various Playlist column names */
  public static final String PLAYLIST_ID_COLUMN = "_id";
  public static final String UP_VOTES_COLUMN = "up_votes";
  public static final String DOWN_VOTES_COLUMN = "down_votes";
  public static final String PRIORITY_COLUMN = "priority";
  public static final String TIME_ADDED_COLUMN ="time_added";
  public static final String SONG_COLUMN = "song";
  public static final String ARTIST_COLUMN = "artist";
  public static final String ALBUM_COLUMN = "album";
  public static final String DURATION_COLUMN = "duration";
  public static final String ADDER_ID_COLUMN = "adder_id";
  public static final String ADDER_USERNAME_COLUMN = "adder_id";

	/** SQL statement for creating the playlist table. */
  private static final String PLAYLIST_TABLE_CREATE = 
    "CREATE TABLE " + PLAYLIST_TABLE_NAME + "("+
		PLAYLIST_ID_COLUMN + " INTEGER PRIMARY KEY , " +
    UP_VOTES_COLUMN + " INTEGER NOT NULL, " +
    DOWN_VOTES_COLUMN + " INTEGER NOT NULL, " +
    PRIORITY_COLUMN + " INTEGER NOT NULL, "  +
    TIME_ADDED_COLUMN + " TEXT NOT NULL, " +
    DURATION_COLUMN + " INTEGER NOT NULL, " +
		SONG_COLUMN + " TEXT NOT NULL, " +
    ARTIST_COLUMN + " TEXT NOT NULL, " + 
    ALBUM_COLUMN + " TEXT NOT NULL,
    ADDER_ID_COLUMN + " INTEGER NOT NULL, " +
    ADDER_USERNAME_COLUMN + " STRING NOT NULL);";

  /** SONG ADD REQUESTS TABLE */

  /** Name of add request table. */
  private static final String ADD_REQUESTS_TABLE_NAME = "add_requests";
  
  /** Constants used for various column names in the song add request table. */
  private static final String ADD_REQUEST_ID_COLUMN = "_id";
  private static final String ADD_REQUEST_LIB_ID_COLUMN = "lib_id";
  private static final String ADD_REQUEST_SYNC_STATUS_COLUMN = "sync_status";

  /** Constants used for the sync status of an add request */
  private static final int ADD_REQUEST_NEEDS_SYNC = 1;
  private static final int ADD_REQUEST_SYNCED = 0;

  /** SQL statement for creating the song add requests table. */
  private static final String ADD_REQUEST_TABLE_CREATE = 
    "CREATE TABLE " + ADD_REQUESTS_TABLE_NAME + "(" +
    ADD_REQUEST_ID_COLUMN + " INTEGER PRIMARY KEY AUTOINCREMENT, " + 
    ADD_REQUEST_LIB_ID_COLUMN + " INTEGER NOT NULL, " +
    ADD_REQUEST_SYNC_STATUS_COLUMN + " INTEGER DEFAULT "+ 
      ADD_REQUEST_NEEDS_SYNC + ", " +
    "CHECK (" + ADD_REQUEST_SYNC_STATUS_COLUMN + "=" + ADD_REQUEST_NEEDS_SYNC +
    "OR " + ADD_REQUEST_SYNC_STATUS_COLUMN + "=" + ADD_REQUEST_SYNCED +
    "));";


	/** Helper for opening up the actual database. */
  private PartyDBHelper dbOpenHelper;

	/**
	 * A class for helping open a PartDB.
	 */
  private class PartyDBHelper extends SQLiteOpenHelper{

		/**
		 * Constructs a new PartyDBHelper object.
		 *
	 	 * @param context The context in which the HostsDBOpenHelper is used.
	 	 */
    PartyDBHelper(Context context){
      super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db){
      db.execSQL(PLAYLIST_TABLE_CREATE);
      db.execSQL(ADD_REQUEST_TABLE_CREATE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion){

    }
  }

  @Override
  public boolean onCreate(){
    dbOpenHelper = new PartyDBHelper(getContext());
    return true;
  }

  @Override
  public String getType(Uri uri){
    return "none";
  }

  @Override
  public int delete(Uri uri, String where, String[] whereArgs){
    if(uri.equals(PLAYLIST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      return db.delete(PLAYLIST_TABLE_NAME, where, whereArgs);
    }
    throw new IllegalArgumentException("Unknown URI " + uri);
  }

  @Override
  public Uri insert(Uri uri, ContentValues initialValues){
    if(uri.equals(PLAYLIST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      long rowId = db.insert(PLAYLIST_TABLE_NAME, null, initialValues);    
      if(rowId >=0){
        return Uri.withAppendedPath(
          PLAYLIST_URI, initialValues.getAsLong(PLAYLIST_ID_COLUMN));
      }
      else{
        return null;
      }
    }
    throw new IllegalArgumentException("Unknown URI " + uri);
  }
  
  @Override
  public Cursor query(Uri uri, String[] projection, 
    String selection, String[] selectionArgs, String sortOrder)
  {
    if(uri.equals(PLAYLIST_URI)){
      SQLiteQueryBuilder qb = new SQLiteQueryBuilder();
      qb.setTables(PLAYLIST_TABLE_NAME);
      SQLiteDatabase db = dbOpenHelper.getReadableDatabase();
      Cursor toReturn = qb.query(
        db, projection, selection, selectionArgs, null,
        null, sortOrder);
      toReturn.setNotificationUri(getContext().getContentResolver(), uri);
      return toReturn;
    }
    throw new IllegalArgumentException("Unknown URI " + uri);
  }

  @Override
  public int update(Uri uri, ContentValues values, String where, 
    String[] whereArgs)
  {
     //TODO implement this
     return 0;
/*    SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
    if(uri.equals(PLAYLIST_URI)){
      int numRowsChanged = 
        db.update(PLAYLIST_TABLE_NAME, values, where, whereArgs);
      return numRowsChanged;
    }
    return 0;*/
  }
}
